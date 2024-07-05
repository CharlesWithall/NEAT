import json
import os

from Defines import get_resource_path
from TestData import TestData

save_dir = os.getenv('APPDATA') + "/NormalisedEssayAssessmentTool/"
save_path = "save_data.json"
default_save_path = "default_save_data.json"
save_dir_and_path = save_dir + save_path

tests_json_attribute = "tests"
statements_json_attribute = "statements"
pass_threshold_attribute = "threshold"
answer_count_json_attribute = "count"
description_json_attribute = "description"
version_json_attribute = "version_number"
display_order_json_attribute = "display_order"

latest_version = 3

class SaveManager:
    __instance = None

    def __init__(self):
        self.__update_to_latest_version()
        self.save_data = self.__load_tests()

        if SaveManager.__instance is not None:
            raise RuntimeError("Cannot instantiate SaveManager. Use 'SaveManager.instance()'")
        else:
            SaveManager.__instance = self

    @staticmethod
    def instance():
        if SaveManager.__instance is None:
            SaveManager()
        return SaveManager.__instance

    def get_test(self, test_name):
        for test in self.save_data:
            if test.name == test_name:
                return test
        return None

    def save_display_order(self, order):
        if not os.path.exists(save_dir_and_path):
            self.__init_save_file()

        with open(save_dir_and_path, 'r+') as f:
            data = json.load(f)
            for i, item in enumerate(order):
                data[tests_json_attribute][item][display_order_json_attribute] = i

            f.seek(0)
            json.dump(data, f)
            f.truncate()

    def save_test(self, test_name, test_description, pass_threshold, test_count, statements_data, display_index):
        if not os.path.exists(save_dir_and_path):
            self.__init_save_file()

        with open(save_dir_and_path, 'r+') as f:
            data = json.load(f)
            if test_name in data[tests_json_attribute]:
                self.delete_test(test_name, False)
            data[tests_json_attribute][test_name] = {}
            data[tests_json_attribute][test_name][description_json_attribute] = test_description
            data[tests_json_attribute][test_name][pass_threshold_attribute] = pass_threshold
            data[tests_json_attribute][test_name][answer_count_json_attribute] = test_count
            data[tests_json_attribute][test_name][statements_json_attribute] = statements_data
            data[tests_json_attribute][test_name][display_order_json_attribute] = display_index

            test_exists = False
            new_test_data = TestData(test_name, test_description, pass_threshold, test_count, statements_data, display_index)
            for i, test in enumerate(self.save_data):
                if test.name == test_name:
                    self.save_data[i] = new_test_data
                    test_exists = True
                    break

            if not test_exists:
                self.save_data.append(TestData(test_name, test_description, pass_threshold, test_count, statements_data, display_index))

            f.seek(0)
            json.dump(data, f)
            f.truncate()

    def delete_test(self, test_name, should_delete_cache=True):
        with open(save_dir_and_path, 'r+') as f:
            data = json.load(f)
            data[tests_json_attribute].pop(test_name)

            if should_delete_cache:
                for item in self.save_data:
                    if test_name == item.name:
                        self.save_data.remove(item)
                        break

            f.seek(0)
            json.dump(data, f)
            f.truncate()

    @staticmethod
    def __load_tests():
        if not os.path.exists(save_dir_and_path):
            SaveManager.__init_save_file()

        with open(save_dir_and_path, 'r+') as f:
            data = json.load(f)
            out_data = []
            for key, value in data[tests_json_attribute].items():
                out_data.append(TestData(key, value[description_json_attribute], value[pass_threshold_attribute],
                                         value[answer_count_json_attribute], value[statements_json_attribute],
                                         value[display_order_json_attribute]))
            return out_data

    @staticmethod
    def __init_save_file():
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        if not SaveManager.__init_default():
            with open(save_dir_and_path, 'w+') as f:
                data = {tests_json_attribute: {}}
                json.dump(data, f)

    @staticmethod
    def __init_default():
        if os.path.exists(save_dir_and_path) or not os.path.exists(get_resource_path(default_save_path)):
            return False

        with open(get_resource_path(default_save_path), 'r') as d:
            default_data = json.load(d)
            with open(save_dir_and_path, 'w+') as f:
                json.dump(default_data, f)
                return True

    @staticmethod
    def __update_to_latest_version():
        if not os.path.exists(save_dir_and_path):
            SaveManager.__init_save_file()

        with open(save_dir_and_path, 'r+') as f:
            data = json.load(f)
            version = 0 if version_json_attribute not in data else data[version_json_attribute]
            while version < latest_version:
                if version == 0:
                    pass
                if version == 1:
                    for test_name in data[tests_json_attribute]:
                        data[tests_json_attribute][test_name][pass_threshold_attribute] = 100
                if version == 2:
                    for i, test_name in enumerate(data[tests_json_attribute]):
                        data[tests_json_attribute][test_name][display_order_json_attribute] = i

                version += 1
                data[version_json_attribute] = version
                f.seek(0)
                json.dump(data, f)
                f.truncate()



