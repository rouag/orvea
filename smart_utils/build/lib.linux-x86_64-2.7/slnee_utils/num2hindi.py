#  -*- coding: utf-8 -*-


def num2hindi(string_number):
    if string_number:
        hindi_numbers = {'0':'٠','1':'١','2':'٢','3':'٣','4':'٤','5':'٥','6':'٦','7':'٧','8':'٨','9':'٩','.':','}
        if isinstance(string_number, unicode):
            hindi_string = string_number.encode('utf-8','replace')
        else:
            hindi_string = str(string_number)
        for number in hindi_numbers:
            hindi_string = hindi_string.replace(str(number),hindi_numbers[number])
        return hindi_string

