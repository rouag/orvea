#  -*- coding: utf-8 -*-

__author__ = 'maddouri'


class ToWord(object):




    def __init__(self, number ):

        self._arabicOnes = ("", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة", "عشرة", "أحد عشر", "اثنا عشر", "ثلاثة عشر", "أربعة عشر", "خمسة عشر", "ستة عشر", "سبعة عشر", "ثمانية عشر", "تسعة عشر")
        self._arabicFeminineOnes = ("", "إحدى", "اثنتان", "ثلاث", "أربع", "خمس", "ست", "سبع", "ثمان", "تسع", "عشر", "إحدى عشرة", "اثنتا عشرة", "ثلاث عشرة", "أربع عشرة", "خمس عشرة", "ست عشرة", "سبع عشرة", "ثماني عشرة", "تسع عشرة")
        self._arabicTens = ("عشرون", "ثلاثون", "أربعون", "خمسون", "ستون", "سبعون", "ثمانون", "تسعون")
        self._arabicHundreds = ("", "مائة", "مئتان", "ثلاثمائة", "أربعمائة", "خمسمائة", "ستمائة", "سبعمائة", "ثمانمائة", "تسعمائة")
        self._arabicAppendedTwos = ("مئتا", "ألفا", "مليونا", "مليارا", "تريليونا", "كوادريليونا", "كوينتليونا", "سكستيليونا")
        self._arabicTwos = ("مئتان", "ألفان", "مليونان", "ملياران", "تريليونان", "كوادريليونان", "كوينتليونان", "سكستيليونان")
        self._arabicGroup = ("مائة", "ألف", "مليون", "مليار", "تريليون", "كوادريليون", "كوينتليون", "سكستيليون")
        self._arabicAppendedGroup = ("", "ألفاً", "مليوناً", "ملياراً", "تريليوناً", "كوادريليوناً", "كوينتليوناً", "سكستيليوناً")
        self._arabicPluralGroups = ("", "آلاف", "ملايين", "مليارات", "تريليونات", "كوادريليونات", "كوينتليونات", "سكستيليونات")
        self.InitializeClass(number )



    def InitializeClass(self, number):
        self.Number = number
        self.ExtractIntegerAndDecimalParts()

    def GetDecimalValue(self, decimalPart):
        return decimalPart #result

    def ExtractIntegerAndDecimalParts(self):
        splits = str(self.Number).split('.')
        self.__intergerValue = long(splits[0])
        # print(self.__intergerValue)
        if len(splits) > 1:
            self.__decimalValue = long(self.GetDecimalValue(splits[1]))

    def ProcessGroup(self, groupNumber):
        tens = groupNumber % 100
        hundreds = groupNumber / 100
        retVal = ""
        if hundreds > 0:
            retVal = "{0} {1}".format( self._englishOnes[hundreds], self._englishGroup[0])
        if tens > 0:
            if tens < 20:
                retVal += (" " if (retVal != "") else "") + self._englishOnes[tens]
            else:
                ones = tens % 10
                tens = (tens / 10) - 2
                retVal += (" " if (retVal != "") else "") + self._englishTens[tens]
                if ones > 0:
                    retVal += (" " if (retVal != "") else "") + self._englishOnes[ones]
        return retVal


    def GetDigitFeminineStatus(self, digit, groupLevel):
        """ <summary>
         Get Feminine Status of one digit
         </summary>
         <param name="digit">The Digit to check its Feminine status</param>
         <param name="groupLevel">Group Level</param>
         <returns></returns>
        """
        if groupLevel == -1: # if it is in the decimal part
            if False : # self.Currency.IsCurrencyPartNameFeminine:
            # 	return self._arabicFeminineOnes[digit]
            # else: # use feminine field
                return self._arabicOnes[digit]
        elif groupLevel == 0:
            if True : #self.Currency.IsCurrencyNameFeminine:
                # print(digit,"-----")
                return self._arabicOnes[digit]
        else:
            return self._arabicOnes[digit]

    def ProcessArabicGroup(self, groupNumber, groupLevel, remainingNumber):
        """ <summary>
         Process a group of 3 digits
         </summary>
         <param name="groupNumber">The group number to process</param>
         <returns></returns>
        """
        tens = groupNumber % 100
        hundreds = int( groupNumber / 100)
        retVal = ""
        if hundreds > 0:
            if tens == 0 and hundreds == 2: # حالة المضاف
                retVal = "{0}".format( self._arabicAppendedTwos[0])
            else: #  الحالة العادية
                retVal = "{0}".format( self._arabicHundreds[hundreds])
        if tens > 0:
            if tens < 20: # if we are processing under 20 numbers
                if tens == 2 and hundreds == 0 and groupLevel > 0: # This is special case for number 2 when it comes alone in the group
                    if self.__intergerValue == 2000 or self.__intergerValue == 2000000 or self.__intergerValue == 2000000000 or self.__intergerValue == 2000000000000 or self.__intergerValue == 2000000000000000 or self.__intergerValue == 2000000000000000000:
                        retVal = "{0}".format( self._arabicAppendedTwos[groupLevel])
                    else: # في حالة الاضافة
                        retVal = "{0}".format( self._arabicTwos[groupLevel])
                else: #  في حالة الافراد # General case
                    if retVal != "":
                        retVal += " و "
                    if tens == 1 and groupLevel > 0 and hundreds == 0:
                        retVal += " "
                    elif (tens == 1 or tens == 2) and (groupLevel == 0 or groupLevel == -1) and hundreds == 0 and remainingNumber == 0:
                        retVal += self.GetDigitFeminineStatus(tens, groupLevel) if self.GetDigitFeminineStatus(tens, groupLevel) else ""
                    else: # Special case for 1 and 2 numbers like: ليرة سورية و ليرتان سوريتان
                        retVal += self.GetDigitFeminineStatus(tens, groupLevel) if self.GetDigitFeminineStatus(tens, groupLevel) else ""
            else: # Get Feminine status for this digit
                ones = tens % 10
                tens = (tens / 10) - 2 # 20's offset
                if ones > 0:
                    if retVal != "":
                        retVal += " و "
                    # Get Feminine status for this digit
                    retVal += self.GetDigitFeminineStatus(ones, groupLevel) if self.GetDigitFeminineStatus(ones, groupLevel) else ""
                if retVal != "":
                    retVal += " و "
                # Get Tens text
                retVal += self._arabicTens[tens]
        return retVal

    def ConvertToArabic(self):
        """ <summary>
         Convert stored number to words using selected currency
         </summary>
         <returns></returns>
        """
        tempNumber = self.Number
        if tempNumber == 0:
            return "صفر"
        # Get Text for the decimal part
        # decimalString = self.ProcessArabicGroup(self.__decimalValue, -1, 0)
        retVal = ""
        group = 0
        while tempNumber >= 1:
            # seperate number into groups
            numberToProcess = (tempNumber % 1000)
            tempNumber = tempNumber / 1000
            # convert group into its text
            groupDescription = self.ProcessArabicGroup(numberToProcess, group, tempNumber )
            if groupDescription != "": # here we add the new converted group to the previous concatenated text
                if group > 0:
                    if retVal != "":
                        retVal = "{0} {1}".format( "و", retVal)
                    if numberToProcess != 2:
                        if numberToProcess % 100 != 1:
                            if numberToProcess >= 3 and numberToProcess <= 10: # for numbers between 3 and 9 we use plural name
                                retVal = "{0} {1}".format( self._arabicPluralGroups[group], retVal)
                            else:
                                if retVal != "": # use appending case
                                    retVal = "{0} {1}".format( self._arabicAppendedGroup[group], retVal)
                                else:
                                    retVal = "{0} {1}".format( self._arabicGroup[group], retVal)
                        else: # use normal case
                            retVal = "{0} {1}".format( self._arabicGroup[group], retVal) # use normal case
                retVal = "{0} {1}".format( groupDescription, retVal)
            group += 1
        formattedNumber = ""
        formattedNumber += retVal if (retVal != "") else ""

        return formattedNumber


def Convert_float(f):
    if f - int(f) > 0 :
        hallala = int(str(f).split('.')[1])
        return  "%s  ريال و  %s" % (ToWord(int(f)).ConvertToArabic(),ToWord(hallala).ConvertToArabic()) + "هللة"
    else :
        return ToWord(int(f)).ConvertToArabic() + "ريال"
# print(ToWord(200).ConvertToArabic())
#print(Convert_float(48888.89))
# print(Convert_float(1.0))
# print Convert_float(4)
