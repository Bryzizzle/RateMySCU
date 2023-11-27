class PDFProcessingError(Exception):
    """ Base Class for exceptions caused by processing the PDF """
    pass


class PDFParseError(PDFProcessingError):
    """ An Exception for when there is an error when parsing the input PDF (Likely Invalid Structure) """
    pass


class MissingElementError(PDFParseError):
    """ An Exception raised when an element is unable to be found while parsing the PDF """
    pass


class ParseVerificationError(PDFParseError):
    """ An Exception raised when the verification of parsed data fails """
    pass
