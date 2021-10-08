from app import db


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text, nullable=True)
    business_activity = db.Column(db.String(120), nullable=True)
    break_evens = db.relationship('BreakEven', backref='company', cascade="all,delete", lazy=True)
    break_even_assessment = db.relationship('BreakEvenAssessment', backref='company', cascade="delete", lazy=True)
    products = db.relationship('Product', backref='company', cascade="all,delete", lazy=True)
    users = db.relationship('User', backref='company', lazy=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first = db.Column(db.String(120), nullable=True)
    last = db.Column(db.String(120), nullable=True)
    admin = db.Column(db.Boolean, nullable=True, default=False)
    investor = db.Column(db.Boolean, nullable=True, default=False)
    onboarding_complete = db.Column(db.Boolean, nullable=True, default=False)
    be_onboarding_complete = db.Column(db.Boolean, nullable=True, default=False)
    pp_onboarding_complete = db.Column(db.Boolean, nullable=True, default=False)


class Bug(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


class BreakEven(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=True)
    code = db.Column(db.String(20), nullable=True)
    risk = db.Column(db.Integer, nullable=True) # 0 Unlikely 1 Low 2 Moderate 3 High

    answers = db.relationship('BreakEvenAnswer', backref="break_even", cascade="all,delete", lazy='subquery')


class BreakEvenAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    break_even_id = db.Column(db.Integer, db.ForeignKey('break_even.id'))
    code = db.Column(db.String(20), nullable=False)
    data = db.Column(db.String(200), nullable=False)


class BreakEvenAssessment(db.Model):
    """the inital assessment, so you can be assigned a risk per BE"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    status = db.Column(db.String(120), nullable=True)

    goals = db.relationship('BreakEvenAssessmentGoal', backref="break_even_assessment", cascade="all,delete", lazy='subquery')

class BreakEvenAssessmentGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    break_even_assessment_id = db.Column(db.Integer, db.ForeignKey('break_even_assessment.id'))
    risk = db.Column(db.String(12), nullable=True)
    code = db.Column(db.String(6), nullable=True)
    saved = db.Column(db.Boolean, nullable=True, default=False)
    answers = db.relationship('BreakEvenAssessmentAnswer', backref="break_even_assessment_goal", cascade="all,delete", lazy='subquery')

class BreakEvenAssessmentAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('break_even_assessment_goal.id'))
    code = db.Column(db.String(20), nullable=True) # question code
    value = db.Column(db.Boolean, nullable=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(20), nullable=True)
    setup_complete = db.Column(db.Boolean, nullable=True, default=False)
    impacts = db.relationship('Impact', backref="product",  cascade="all,delete")
    facets = db.relationship('ProductFacet', backref="product",  cascade="all,delete")
    product_properties = db.relationship('ProductProperty', backref="product",  cascade="all,delete")

    def __repr__(self):
        return '<Product %r>' % self.name


class ProductFacet(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(80), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))


class ProductProperty(db.Model):
    """
    property - refers to the 'Properties' tab, ie X, X1, X2, etc
    ie, this is a link between the Product & all the Identification answers
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(80), nullable=False)  # property code
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))

    answers = db.relationship('ProductPropertyAnswer', cascade="all,delete", backref="product_property")


class ProductPropertyAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(80), nullable=False)
    product_property_id = db.Column(db.Integer, db.ForeignKey('product_property.id'))


class Impact(db.Model):
    """
    so, it's unique on PP action + Option text (not the option number)
    the result of doing Setup & 2 and then having your actions mapped
    save pp action, text, SDGs
    where do we want to save the data from the survey that links to this tho?
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))

    property_code = db.Column(db.String(80), nullable=False)  # property code
    pp_action = db.Column(db.String(80), nullable=False)  # ie PP01.01
    option_code = db.Column(db.String(80), nullable=False)
    option_text = db.Column(db.String(500), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

    sdgs = db.relationship('ImpactSdg', backref="impact",  cascade="all,delete")
    answers = db.relationship('ImpactAnswer', backref="impact", cascade="all,delete", lazy='subquery')


class ImpactSdg(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sdg = db.Column(db.String(80), nullable=False)
    impact_id = db.Column(db.Integer, db.ForeignKey('impact.id'))


class ImpactAnswer(db.Model):
    """
    so, it's unique on PP action + Option text (not the option number)
    the result of doing Setup & 2 and then having your actions mapped
    save pp action, text, SDGs
    where do we want to save the data from the survey that links to this tho?
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    impact_id = db.Column(db.Integer, db.ForeignKey('impact.id'))

    # ie A-2
    number = db.Column(db.String(20), nullable=False)
    data = db.Column(db.String(200), nullable=True)  # going to be code or the number or string
    # for 14&16 they want to enter paragraphs..
    text = db.Column(db.Text, nullable=True)
