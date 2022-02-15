import unittest
from main import validate_license


# Так как на вход в любом случае приходят сообщения, которые уже очищены от пробелов и все буквы поставлены в Uppercase
# Данные тесты рассматривают только такой вариант развития

class TestValidateLicense(unittest.TestCase):

    def test_1(self):
        self.assertEqual(validate_license(""), False)

    def test_2(self):
        self.assertEqual(validate_license("WEIGH"), False)

    def test_3(self):
        self.assertEqual(validate_license("A1264AA1"), False)

    def test_4(self):
        self.assertEqual(validate_license("AA1JAB23"), False)

    def test_5(self):
        self.assertEqual(validate_license("A000AA00"), False)

    def test_6(self):
        self.assertEqual(validate_license("A000AA01"), False)

    def test_7(self):
        self.assertEqual(validate_license("A001AA01"), True)

    def test_8(self):
        self.assertEqual(validate_license("Z001AA01"), False)

    def test_9(self):
        self.assertEqual(validate_license("Б001AA01"), False)

    def test_10(self):
        self.assertEqual(validate_license("Х666ЕР69"), True)

    def test_11(self):
        self.assertEqual(validate_license("А222АА22"), True)

    def test_12(self):
        self.assertEqual(validate_license("}001AA01"), False)

    def test_13(self):
        self.assertEqual(validate_license("Х001;%01"), False)

    def test_14(self):
        self.assertEqual(validate_license("AOO1AA01"), False)

    def test_15(self):
        self.assertEqual(validate_license(None), False)


if __name__ == '__main__':
    unittest.main()
