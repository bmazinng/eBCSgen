import unittest
import requests
from Parsing.ParseBCSL import Parser


class TestModel(unittest.TestCase):
    def setUp(self):
        self.model_parser = Parser("model")
        self.url = 'http://localhost:5000/bcsl_parse'

        self.model_wrong_1 = \
            """#! rules
            X(K{i})::rep => X(K{p})::rep @ k1*[X()::rep]
            X(T{a})::rep => X(T{o}):;rep @ k2*[Z()::rep]
            => Y(P{f})::rep @ 1/(1+([X()::rep])**4)

            #! inits
            2 X(K{c}, T{e}).X(K{c}, T{j})::rep
            Y(P{g}, N{l})::rep

            #! definitions
            k1 = 0.05
            k2 = 0.12
            """

        self.model_with_complexes = """
            #! rules
            // commenting
            X(T{a}):XX::rep => X(T{o}):XX::rep @ k2*[X().X()::rep]
            K{i}:X():XYZ::rep => K{p}:X():XYZ::rep @ k1*[X().Y().Z()::rep] // also here
            => P{f}:XP::rep @ 1/(1+([X().P{_}::rep])**4) // ** means power (^)

            #! inits
            // here
            2 X(K{c}, T{e}).X(K{c}, T{j})::rep
            Y(P{g}, N{l})::rep // comment just 1 item

            #! definitions
            // and
            k1 = 0.05 // also
            k2 = 0.12

            #! complexes
            XYZ = X().Y().Z() // a big complex
            XX = X().X()
            XP = X().P{_}
            """

    def test_remote_request(self):
        try:
            response = requests.get('http://localhost:5000/ping')
            self.assertTrue(response.status_code == 200)
        except requests.exceptions.ConnectionError:
            raise AssertionError("API not available")

    def test_remote_parsing_model(self):
        try:
            # correct one
            result_local = self.model_parser.syntax_check(self.model_with_complexes)

            response = requests.post(self.url, {'start': 'model', 'expression': self.model_with_complexes})
            result_remote = eval(response.text)

            self.assertEqual(result_remote['success'], result_local.success)
            self.assertEqual(result_remote['data'], str(result_local.data))

            # wrong one
            result_local = self.model_parser.syntax_check(self.model_wrong_1)

            response = requests.post(self.url, {'start': 'model', 'expression': self.model_wrong_1})
            result_remote = eval(response.text)

            self.assertEqual(result_remote['success'], result_local.success)
            self.assertEqual(eval(result_remote['data']), result_local.data)
        except requests.exceptions.ConnectionError:
            raise AssertionError("API not available")