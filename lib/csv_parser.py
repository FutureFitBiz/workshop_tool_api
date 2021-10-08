import csv
import lib.excel_parser as excel_parser

file_paths = {
    'add_edit_product': 'data/Add Edit Activity.csv',
    'be_short_names': 'data/short_and_full_names/Break-Even Goals-Table 1.csv',
    'pp_short_names': 'data/short_and_full_names/Positive Pursuits  Actions-Table 1.csv',
    'facets': 'data/facet_and_properties/F Facets-Table 1.csv',
    'properties': 'data/facet_and_properties/X Properties -Table 1.csv',
    'descriptions': 'data/facet_and_properties/D Descriptions-Table 1.csv',
    'x_base_path': 'data/facet_and_properties',
    'X0': 'X0 Automatic-Table 1.csv',
    'X1': 'X1 Energy-Table 1.csv',
    'X2': 'X2 Water-Table 1.csv',
    'X3': 'X3 Natural Resources-Table 1.csv',
    'X4': 'X4 Pollution-Table 1.csv',
    'X5': 'X5 Waste-Table 1.csv',
    'X6': 'X6 Ecosystems-Table 1.csv',
    'X7': 'X7 People-Table 1.csv',
    'X8': 'X8 Economies-Table 1.csv',
    'impact_data': 'data/Impact Metrics.csv',
    'be_base_path': 'data/be/',
    'be_sdgs': 'data/be/SDG Links-Table 1.csv',
    'business_activity_questions': 'data/business_activity_questions.csv',
    'heatmap_template_questions': 'data/heatmap_template_questions.csv',
}


class Surveys():
    def __init__(self):
        self.facets = {}
        self.properties = {}
        self.add_edit_product = {}
        self.pp_action = {}
        self.pp_descriptions = {}
        self.pp_text_lookup = {}
        self.be = {}
        self.be_tags = []
        self.be_text_lookup = {}
        self.be_sdgs = {}
        self.x0 = []
        self.facet_description_lookup = {}
        self.property_description_lookup = {}
        self.property_title_lookup = {}
        self.value_template = "{}-{}"
        self.option_template = "{}-{}.{}"
        self.business_activity_questions = {}
        self.heatmap_template_questions = {}
        self.heatmaps = {}
        self.sdg_to_be_tooltips = {}

    def load(self):
        # first do these
        self.load_be_tags()
        self.load_pp_descriptions()

        self.load_x0_automatic()
        self.load_facets()
        self.load_facet_description_lookup()
        self.load_pp_text_lookup()
        self.load_be_text_lookup()
        self.load_properties()  # this loads all X1-8 tabs too
        self.load_property_description_lookup()
        self.load_action()
        self.load_add_edit_product()
        self.load_be_sdgs()
        self.load_be()
        self.load_sdg_to_be_tooltips()

        self.load_heatmap_template_questions()
        # heatmaps after the heatmap template - becuase of codes
        self.load_heatmaps(self.heatmap_template_questions)
        # after heatmaps do the options (so we can grey out unavailable ones)
        self.load_business_activity_questions()

    def load_facets(self):
        self.facets = {
            'questions': self.load_questions('F', file_paths['facets'])
        }

    def load_add_edit_product(self):
        self.add_edit_product = {
            'questions': self.load_questions('AE', file_paths['add_edit_product'])
        }

    def load_be_tags(self):
        tags = []
        for i in range(23):
            n = i + 1
            if n < 10:
                tags.append('BE0' + str(n))
            else:
                tags.append('BE' + str(n))
        self.be_tags = tags

    def load_business_activity_questions(self):
        """
        aka, the 2-3 dropdowns of options for the purpose of selecting a final option, which ties to a heatmap
        """
        self.business_activity_questions = excel_parser.new_business_activity_questions()


    def load_heatmap_template_questions(self):
        """
        each of the 23 goals, has 10+ questions that we use to judge the goal risk level
        ^if you select a heatmap, these answers will be pre populated from the heatmap
        """
        # split into two dicts,
        # one for all the unique questions
        # one for the layout, (ie, some goals have duplicate questions from other goals)
        layout = {}
        questions = {}
        curren_be_code = ''
        question_count = 1

        self.heatmap_template_questions = excel_parser.parse_heatmap_template()


    def load_heatmaps(self, heatmap_template_questions):
        print('loading heatmaps v2')
        self.heatmaps = excel_parser.parse_heatmaps(heatmap_template_questions)


    def load_be(self):
        for tag in self.be_tags:
            path = file_paths['be_base_path'] + tag + '-Table 1.csv'
            self.be[tag] = {
                'questions': self.load_questions(tag, path),
                'scores': self.load_scores(tag, path)
            }

    def load_be_sdgs(self):
        with open(file_paths['be_sdgs'], 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            lookup = {}
            next(reader)
            next(reader)
            for row in reader:

                if row[1]:
                    sdgs = row[2].split(',')
                    sdgs = [int(x.strip()) for x in sdgs]
                    lookup[row[1].strip()] = sdgs

            self.be_sdgs = lookup

    def load_scores(self, tag, path):
        with open(path, 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            started = False
            scores = {}
            current = ''

            for row in reader:
                col_a = row[0].strip().lower()
                if started and col_a == 'end':
                    break

                if col_a == 'score':
                    started = True

                if started:
                    col_c = row[2].strip().lower()
                    col_d = row[3].strip()
                    if col_c == 'type':
                        current = col_d
                        scores[col_d] = {}
                    if col_c == 'score':
                        scores[current]['score'] = col_d
                    if col_c == 'unit':
                        scores[current]['unit'] = col_d

            return scores

    def load_pp_descriptions(self):
        with open(file_paths['descriptions'], 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            next(reader)
            next(reader)
            lookup = {}

            for row in reader:
                option = row[1].strip()
                action = row[2].strip()
                text = row[3].strip()
                key = "{}-{}".format(action, option)
                lookup[key] = text

        self.pp_descriptions = lookup

    def load_facet_description_lookup(self):
        for facet in self.facets['questions']:
            if 'options' in facet:
                for option in facet['options']:
                    self.facet_description_lookup[option['value']] = option['title']

    def _load_keys(self, values):
        for option in values['options']:
            self.property_description_lookup[option['value']] = option['title']
            if 'options' in option:
                self._load_keys(option)

    def load_property_description_lookup(self):
        for property in self.properties['questions']:
            if 'options' in property:
                self._load_keys(property)

        self.property_description_lookup['X-0'] = 'Automatic'
        for option in self.x0:
            self.property_description_lookup[option['value']] = option['title']

    def load_pp_text_lookup(self):
        with open(file_paths['pp_short_names'], 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            next(reader)

            for row in reader:
                if row[0]:
                    self.pp_text_lookup[row[0]] = row[1]
                elif row[2]:
                    self.pp_text_lookup[row[2]] = row[3]

    def load_be_text_lookup(self):
        lookup = {
            # lookup by break even code, ie BE02
            'break_evens': {},
            # for the front end side bar, with paths etc
            'menu_items': [],
            # reverse lookup of menuitem path to BE, might not need?
            'menu_item_to_be': {},
            'be_order': {},
        }
        category = {}

        # so we can sort by, loop through, and get the next available
        order = 0
        category_order = 0
        current = ''

        with open(file_paths['be_short_names'], 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            next(reader)
            next(reader)
            next(reader)

            for row in reader:
                col_a = row[0].strip().lower()
                be = row[2].strip().upper()

                if col_a == 'end':
                    if category:
                        lookup['menu_items'].append(category)

                if col_a == 'title':
                    if category:
                        lookup['menu_items'].append(category)
                    category_order += 1
                    category = {
                        'path': row[1].lower().replace(' ', '_'),
                        'title': row[1],
                        'items': [],
                        'order': category_order,
                        'description': []
                    }

                if category and current == 'description' and be == '':
                    category['description'].append(row[1])

                if col_a == 'description':
                    current = 'description'
                    category['description'].append(row[1])

                if row[1] == '':
                    current = ''

                if category and be != '':
                    short_name = row[3].strip()
                    middle_name = row[4].strip()
                    long_name = row[5].strip()
                    short_path = short_name.lower().replace(' ', '_')
                    order += 1

                    lookup['break_evens'][be] = {
                        'short_name': short_name,
                        'middle_name': middle_name,
                        'long_name': long_name,
                        'category': category['title'],
                        'category_path': category['path'],
                        'path': short_path,
                        'order': order,
                    }

                    category['items'].append({
                        'code': be,
                        'path': short_path,
                        'long_name': long_name,
                        'category': category['title'],
                        'category_path': category['path'],
                        'title': short_name,
                        'order': order,
                    })
                    lookup['menu_item_to_be'][short_path] = be
                    lookup['be_order'][be] = order

        self.be_text_lookup = lookup

    def load_x0_automatic(self):
        self.x0 = self.load_x_tab('X0')
        self.property_title_lookup['X-0'] = 'Automatic'

    def load_properties(self):
        x_description = []
        properties = {
            'questions': self.load_questions('X', file_paths['properties'])
        }

        with open(file_paths['properties'], 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            one_more = False
            for row in reader:
                if row[2] == 'x description' or one_more:
                    one_more = not one_more
                    x_description.append(row[3])

        for i, item in enumerate(properties['questions'][1]['options']):
            # the first 'question' is the title & header of the tab
            properties['questions'].append({
                'logic': [[item['value']]],
                'type': '',
                'title': item['title'],
                'description': x_description,
            })

            self.property_title_lookup[item['value']] = item['title']

            properties['questions'].append({
                'logic': [[item['value']]],
                'type': 'checkbox',
                'options': self.load_x_tab('X' + str(i + 1))
            })

        self.properties = properties

    def load_x_tab(self, x_number):
        """
        how it's laid out in the frontend (so we can loop thorugh easily)
        first section is just a larger title/description

        {
            'logic': 'X.2',
            'value': 'X2',
            'type': 'section',
            'title': "Water",
            'text': ["these are", "looped as paragraphs <p></p>"],
        },

        logic - hide/show based on the initial properties 'X' question
        options - all of the checkboxes per X1-8, nested in the same way as the excel
        value - unique per option, combination of X' plus option

        {
            'logic': 'X2',
            'description': "",
            'type': 'checkbox',
            'options': [{
                'value': 'X2-1',
                'title': 'Helping others improve their water-use efficiency',
                'options': [ {
                    'value': 'X2-1.1',
                    'title': "Water management by local communities",
                  },

             },
        }
        """
        loaded_rows = []
        tab_path = '{}/{}'.format(file_paths['x_base_path'], file_paths[x_number])

        with open(tab_path, 'r') as csv_file:
            """
            1.grab all the rows,
            2.go through and deal with any sdg/action only rows
            3.re strucutre for frontend, so we get nested options
            """
            reader = csv.reader(csv_file, delimiter=',')

            next(reader)  # blank line
            next(reader)  # column headers

            for row in reader:
                facets = []
                actions = []
                sdg = ''
                option = ''
                option_text = ''

                # get all the 'F' facet options
                for i, x in enumerate(row[1:8]):
                    # the two F2 Columns (C & D (2&3)) are an 'or', everything else is &
                    if x:
                        # change it to be the same as wot getz imported from the 'properties' tab
                        x = x[:1] + '-' + x[1:]
                        facets.append(x)

                # get the option if there is one
                # ie '2.1.1'
                # should always be 1 per row
                for x in [8, 10, 12, 14, 16]:
                    if row[x]:
                        option = row[x]
                        option_text = row[x + 1]

                # always 1 sdg per row
                sdg = row[21]

                # get the PP actions (potentially 3)
                # all will have the same SDG that is on the row
                for x in [18, 19, 20]:
                    if row[x]:
                        actions.append({
                            'pp': row[x],
                            'sdgs': [sdg],
                            'facets': facets
                        })

                to_add = {
                    'facets': facets,
                    'actions': actions,
                    'option': option,
                    'title': option_text
                }

                loaded_rows.append(to_add)

        updated_rows = []

        # second part

        # now we hae all the data, run through and crunch all the blank ones
        # we do this because of they way they put it line by line in the excel

        for row in loaded_rows:
            # if it has an option, we can add to new list,
            # any rows without an option will go in the last option row
            if row['option']:
                updated_rows.append(row)

            # no option, so merge it up
            else:
                for action in row['actions']:
                    # find all actions that have matching PP & facets
                    last_option_row = updated_rows[-1]

                    if len(last_option_row['actions']) == 0:
                        # if there isnt one, just add it
                        last_option_row['actions'].append(action)
                        continue

                    # otherwise, run through the current actions,
                    # merge into the first matching one
                    # else add
                    matched = False

                    for i, previous_action in enumerate(last_option_row['actions']):
                        pp_match = previous_action['pp'] == action['pp']
                        facet_match = sorted(previous_action['facets']) == sorted(action['facets'])

                        if pp_match and facet_match:
                            # merge sdgs
                            matched = True
                            sdgs = list(set(previous_action.get('sdgs', []) + action.get('sdgs', [])))
                            last_option_row['actions'][i]['sdgs'] = sdgs
                            break

                    if not matched:
                        last_option_row['actions'].append(action)

        # there should be no blanks now, so we can nest them
        nested_rows = []
        # use the dots to judge depth
        # '1' count == 0, so level 1,
        # '1.1' count == 1, so level 2,
        # '1.1.2' count == 2, so level 3,
        # '1.1.2.2' count == 3, so level 4,
        # '1.1.2.2.4' count == 4, so level 5,

        for row in updated_rows:
            # add bits for frontend
            row['value'] = '{}-{}'.format(x_number, row['option'])
            row['type'] = 'checkbox'
            row['options'] = []

            dots = row['option'].count('.')

            if dots == 0:
                nested_rows.append(row)
            elif dots == 1:
                nested_rows[-1]['options'].append(row)
            elif dots == 2:
                nested_rows[-1]['options'][-1]['options'].append(row)
            elif dots == 3:
                nested_rows[-1]['options'][-1]['options'][-1]['options'].append(row)
            elif dots == 4:
                nested_rows[-1]['options'][-1]['options'][-1]['options'][-1]['options'].append(row)
            # ...ugh ok

        return nested_rows

    def load_action(self):
        """
        data collection & intensity
        """
        data_colection = self.load_questions('A', file_paths['impact_data'])

        data = {
            'title': '',
            'description': '',
            'questions': data_colection
        }
        self.pp_action = data
        # merge em?

    def load_questions(self, identifier,  file_path):
        questions = []
        question = {}
        next_logic = []
        current = ''

        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')

            for row in reader:
                col_a = row[0].lower().strip()
                col_b = row[1].lower().strip()
                col_c = row[2].lower().strip()
                col_d = row[3]  # aka where the actual values mostly are

                if col_a == 'end':
                    questions.append(question)
                    break

                elif col_a == 'if' or col_a == 'and':
                    current = 'if'
                    logic = self._format_question_logic(col_b, identifier)
                    next_logic.append(logic)

                elif col_c == 'no.':
                    if question:
                        questions.append(question)
                    current = 'no.'
                    question = self._new_question(col_d, next_logic, identifier)
                    next_logic = []

                elif col_c == 'title' or col_c == 'heading 1' or col_c == 'heading 2':
                    current = 'title'
                    question['title'] = col_d

                elif col_c == 'description':
                    current = 'description'
                    question['description'].append(col_d)

                elif col_c == '' and current == 'description':
                    if row[3] != '':
                        question['description'].append(col_d)

                elif col_c == 'type':
                    current = 'type'
                    question['type'] = self._get_question_type(col_d)

                elif col_c == 'sub type':
                    current = 'sub type'
                    question['sub_type'] = col_d

                elif col_c == 'score':
                    current = 'score'

                elif col_c == 'unit' and current != 'score':
                    current = 'unit'
                    question['unit'] = col_d

                elif col_c == 'option text':
                    current = 'options'
                    for i, x in enumerate(row[3:], 1):
                        if x != '':
                            question['options'].append({
                                'title': x,
                                'value': self.option_template.format(identifier, question['number'], str(i))
                            })
                elif col_c == 'help text':
                    current = 'help_text'
                    for i, x in enumerate(row[3:]):
                        if x != '':
                            question['options'][i]['help_text'] = x

                elif col_c == 'option description':
                    current = 'option description'
                    for i, x in enumerate(row[3:]):
                        if x != '':
                            question['options'][i]['description'] = x

                elif col_c == 'value':
                    current = 'option value'
                    for i, x in enumerate(row[3:]):
                        if x != '':
                            question['options'][i]['option_value'] = x

        return questions

    def _format_question_logic(self, text, identifier):
        logic_array = text.replace(' ', '').split(',')
        formatted_logic = []
        for x in logic_array:
            if '-' in x:
                formatted_logic.append(x)
            else:
                formatted_logic.append(self.value_template.format(identifier, x))
        return formatted_logic

    def _new_question(self, text, next_logic, identifier):
        if text.lower() == 'n/a':
            # it's just an info section, not really a question
            question = {
                'type': 'section',
                'logic': next_logic,
                'description': []
            }
        else:
            question = {
                'number': text,
                'logic': next_logic,
                'description': [],
                'options': [],
                'value': self.value_template.format(identifier, text)
            }
        return question

    def _get_question_type(self, text):
        type = text.lower().strip()
        if type == 'options (single)':
            type = 'radio'
        elif type == 'options (multiple)':
            type = 'checkbox'

        return type


    def load_sdg_to_be_tooltips(self):
        file = 'data/SDG to BE Goal Tooltips.csv'
        break_evens = {}
        with open(file, 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            # print(reader)
            next(reader)
            # col 2+ are the sdgs, ie ['', '', 'SDG 1',..
            for row in reader:
                # print('----')
                break_even = row[1]
                title = row[0] == 'Heading'
                break_evens[break_even] = {}
                # print(row[0])
                if not title:
                    for i in range(2, 19):
                        # print(row[i])
                        break_evens[break_even][str(i - 1)] = row[i]
                # break

        self.sdg_to_be_tooltips = break_evens
