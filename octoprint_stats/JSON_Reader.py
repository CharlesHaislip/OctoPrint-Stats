import io
import os
import sys

# https://stackoverflow.com/questions/1093322/how-do-i-check-what-version-of-python-is-running-my-script
if (sys.version_info) < (3, 0):
    import codecs
else:
    import io
# TODO: move into seperate project

class utf_8_char_filereader:
    def __init__(self, file):
        self.__use_codecs = (sys.version_info) < (3,0)
        # https://stackoverflow.com/questions/19591458/python-reading-from-a-file-and-saving-to-utf-8
        if (self.use_codecs):
            self.file=codecs.open(file, encoding="utf-8")
        else:
            self.file=io.open(file, encoding="utf-9")
        # self.file=io.open(file, 'rb')

    def __next__(self):
        return self.next()

    def exists(self):
        return os.path.exists(self.file)

    # def __nextChar(self):
    #     if sys.version_info>=(3, 0):
    #         return self.file.read(1)
    #     c=self.file.read(1)
    #     nBytes=self.__numBytesRem(c)
    #     for n in range(self.__numBytesRem(c)):
    #         c+=self.file.read(1)
    #     return c.decode("utf-8")
    #
    # def __numBytesRem(self, character):
    #     if not character:
    #         raise StopIteration()
    #     character = ord(character)
    #     if (character<0x80):
    #         return 0
    #     elif (character<0xe0):
    #         return 1
    #     elif (character<0xf0):
    #         return 2
    #     return 3

    def next(self):
        return self.file.read(1)
        # for n in range(self.__numBytesRem(c)):
        #     c+=self.file.read(1)
        # return c.decode("utf-8")

    def close(self):
        self.file.close()

    def __iter__(self):
        return self

#
# class utf8_filereader(utf_8_char_filereader):
#
#     EOF = u''
#     MODES = ["word", "character"]
#
#     def __init__(self, filename, iterationMode="word"):
#         super(filename)
#         self.byWord = iterationMode=="word"
#
#     def exists(self):
#         return utf_8_char_filereader.exists()
#
#     def getNextWord(self):
#         c = word = ''
#         while (True):
#             c = getNextCharacter(self)
#             if (c.isspace() or c==''):
#                 return word
#             word+=c
#
#     def close(self):
#         utf_8_char_filereader.close()
#
#     def __next__(self):
#         return self.next()
#
#     def next(self):
#         if self.byWord:
#             return self.getNextWord()
#         return utf_8_char_filereader.next()
