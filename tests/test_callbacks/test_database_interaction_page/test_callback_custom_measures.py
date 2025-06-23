from src.callbacks.database_interaction_page.callback_custom_measure import convert_custom_table_to_input, \
    upload_csv_and_add_measure
from contextvars import copy_context

class TestCallbackCustomMeasure:
    def test_convert_custom_table_to_input(self):
        row_data = [['measure,dijkvak,mechanism,tijd,Kosten,Betrouwbaarhaid'],
                    ['ROCKS,1,Stabiliteit,40,2000,3.3'],
                    ['ROCKS,1,Stabiliteit,0,2000,4']]

        custom_measure_list = convert_custom_table_to_input(row_data)
        assert isinstance(custom_measure_list, list), "The output should be a list"

    def test_upload_csv_and_add_measure_faulty_header(self):
        str_content = "data:application/vnd.ms-excel;base64,bWVhc3VyZSxkaWprdmFrLG1lY2hhbmlzbSx0aWpkLEtvc3RlbixCZXRyb3V3YmFhcmhhaWQNCkFCQyxXc05vb19TdGFiXzAxMTYwMF8wMTIwMDAsU3RhYmlsaXRlaXQsNjAsMjAwMCwzLjMNCkFCQyxXc05vb19TdGFiXzAxMTYwMF8wMTIwMDAsU3RhYmlsaXRlaXQsMCwyMDAwLDk5DQpBQkNwaXBwcCxXc05vb19TdGFiXzAxMTYwMF8wMTIwMDAsUGlwaW5nLDIwLDIwMDAsODANCkFCQ3BpcHBwLFdzTm9vX1N0YWJfMDExNjAwXzAxMjAwMCxQaXBpbmcsMCwyMDAwLDgwDQoNCg=="
        vr_config = {'traject': '31-1', 'T': [0, 19, 20, 25, 50, 75, 100],
                     'excluded_mechanisms': ['HYDRAULIC_STRUCTURES'], 'input_database_name': 'vrtool_input.db',
                     'input_directory': 'C:\\Users\\hauth\\OneDrive - Stichting Deltares\\Documents\\tempo\\VRM\\renewal custom measure tables',
                     'output_directory': 'C:\\Users\\hauth\\OneDrive - Stichting Deltares\\Documents\\tempo\\VRM\\renewal custom measure tables\\res'}


        def run_callback():
            return upload_csv_and_add_measure(str_content, vr_config)

        ctx = copy_context()
        output = ctx.run(run_callback)
        assert isinstance(output, tuple), "The output should be a tuple"

    def test_upload_csv_and_add_measure_correct_header(self):
        vr_config = {'traject': '31-1', 'T': [0, 19, 20, 25, 50, 75, 100],
                     'excluded_mechanisms': ['HYDRAULIC_STRUCTURES'], 'input_database_name': 'vrtool_input.db',
                     'input_directory': 'C:\\Users\\hauth\\OneDrive - Stichting Deltares\\Documents\\tempo\\VRM\\renewal custom measure tables',
                     'output_directory': 'C:\\Users\\hauth\\OneDrive - Stichting Deltares\\Documents\\tempo\\VRM\\renewal custom measure tables\\res'}

        str_content = "data:application/vnd.ms-excel;base64,bWFhdHJlZ2VsZW4sZGlqa3ZhayxtZWNoYW5pc20sdGlqZCxrb3N0ZW4sYmV0YQ0KQUJDZHJkZHIsV3NOb29fU3RhYl8wMTE2MDBfMDEyMDAwLFN0YWJpbGl0ZWl0LDYwLDIwMDAsMy4zDQpBQkNkcmRkcixXc05vb19TdGFiXzAxMTYwMF8wMTIwMDAsU3RhYmlsaXRlaXQsMCwyMDAwLDk5DQpBQkNwaXBwcHAsV3NOb29fU3RhYl8wMTE2MDBfMDEyMDAwLFBpcGluZywyMCwyMDAwLDgwDQpBQkNwaXBwcHAsV3NOb29fU3RhYl8wMTE2MDBfMDEyMDAwLFBpcGluZywwLDIwMDAsODANCg0K"

        def run_callback():
            return upload_csv_and_add_measure(str_content, vr_config)

        ctx = copy_context()
        output = ctx.run(run_callback)
        assert isinstance(output, tuple), "The output should be a tuple"
