

from src.callbacks.database_interaction_page.callback_custom_measure import convert_custom_table_to_input


class TestCallbackCustomMeasure:
    def test_convert_custom_table_to_input(self):

        row_data = [['measure,dijkvak,mechanism,tijd,Kosten,Betrouwbaarhaid'],
                    ['ROCKS,1,Stabiliteit,40,2000,3.3'],
                    ['ROCKS,1,Stabiliteit,0,2000,4']]

        custom_measure_list = convert_custom_table_to_input(row_data)
        assert isinstance(custom_measure_list, list), "The output should be a list"
