from enum import Enum

MAX_USER_LEN = 32
VALID_SEPARATORS = {'-', '_'}


class UsernameType(Enum):
    valid = None
    too_long = f"The username exceeds the {MAX_USER_LEN} character limit"
    not_ascii = f"The username must only contain ASCII characters"
    not_lowercase = "The username must be lowercase"
    has_invalid_chars = "Only alpha-numeric characters, '-' and '_' allowed"
    

def validate_username(username: str) -> UsernameType:
    not_alphanum_chars = {i for i in username if not i.isalnum()}

    if len(username) > MAX_USER_LEN:
        return UsernameType.too_long
    elif not username.isascii():
        return UsernameType.not_ascii
    elif not username.islower():
        return UsernameType.not_lowercase
    elif (not_alphanum_chars <= VALID_SEPARATORS) is False:
        return UsernameType.has_invalid_chars
    
    return UsernameType.valid