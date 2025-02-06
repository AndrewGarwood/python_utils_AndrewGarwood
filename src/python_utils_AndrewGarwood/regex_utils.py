from typing import List, Tuple, Optional
import re
from pandas import Series

__all__ = [
    'extract_leaf', 'ahead_is', 'ahead_not', 'behind_is', 'behind_not',
    'equivalent_alphanumeric', 'equivalent_alphanumeric_split_set', 'extract_unit_measurements',
    'extract_dimensions', 'extract_name_from_address', 'extract_phone', 'extract_zip', 'extract_state',
    'extract_city', 'STATE_ABBREVIATIONS', 'STATE_NAMES', 'street_suffix_pattern', 'street_suffix_list',
    'suite_pattern', 'name_suffixes', 'number_pattern', 'units', 'dimension_symbol_pattern'
]

def extract_leaf(s: str, delimiter: str = ':') -> str:
    """
    Extract the last part of a string separated by a delimiter.

    Args:
        s (str): _description_
        delimiter (str, optional): _description_. Defaults to ':'.

    Returns:
        str: _description_
    
    Example:
    key1 and key2 are permutations of the same item SKU
        key1 = parentClass1:childClass1:leaf
        key2 = parentCLass2:leaf
        extract_leaf(key1) -> 'leaf'
        extract_leaf(key2) -> 'leaf'
    
    """
    return s.rsplit(delimiter, 1)[-1] if delimiter in s else s

def ahead_is(*args: str) -> str:
    return rf'(?={'|'.join(arg for arg in args)})'

def ahead_not(*args: str) -> str:
    return '|'.join(rf'(?!{arg})' for arg in args)

def behind_is(*args: str) -> str:
    return rf'(?<={'|'.join(arg for arg in args)})'

def behind_not(*args: str) -> str:
    return '|'.join(rf'(?<!{arg})' for arg in args)

def equivalent_alphanumeric(
    s1: str, 
    s2: str, 
    case_sensitive: bool = False
) -> bool:
    s1 = re.sub(r'[\[\]\(\)\s]', '', s1)
    s2 = re.sub(r'[\[\]\(\)\s]', '', s2)
    if not case_sensitive:
        s1 = s1.casefold()
        s2 = s2.casefold()
    return s1 == s2

def equivalent_alphanumeric_split_set(
    s1: str, 
    s2: str, 
    delimiter: str = ' ', 
    case_sensitive: bool = False
) -> bool:
    """_summary_

    Args:
        s1 (str): _description_
        s2 (str): _description_
        delimiter (str, optional): _description_. Defaults to ' ' (space).
        case_sensitive (bool, optional): _description_. Defaults to False.

    Returns:
        bool: _description_
    Motivating Example:
    >>> s1 = "an apple fell"
    >>> s2 = "fell an apple"
    >>> set1 = set(s1.split())
    >>> set1
    {'an', 'apple', 'fell'}
    >>> set2 = set(s2.split())
    >>> set2
    {'an', 'apple', 'fell'}
    >>> set1 == set2
    True
    """
    if not case_sensitive:
        s1 = s1.casefold()
        s2 = s2.casefold()
    s1 = re.sub(r'[\[\]\(\)\s]', '', s1)
    s2 = re.sub(r'[\[\]\(\)\s]', '', s2)
    return set(s1.split(delimiter)) == set(s2.split(delimiter))

def extract_unit_measurements(s: str) -> Tuple[str, List[str]]:
    if not s or s in ['nan', '']:
        return []
    # modified_s: str = s
    measurements: List[str] = []
    for unit in units:
        if '[' in s or ']' in s:  # already extracted measurements
            break
        unit_measurement_pattern: str = rf'{behind_not(dimension_symbol_pattern)}{number_pattern} ?{unit}{ahead_not(dimension_symbol_pattern)}'
        matches: List[str] = re.findall(unit_measurement_pattern, s)
        s = re.sub(unit_measurement_pattern, '', s).replace('(', '').replace(')', '').strip()
        for match in matches:
            if not re.search(r'\d ' + unit, match):
                corrected_match = re.sub(r'(\d)' + unit, r'\1 ' + unit, match)
                measurements.append(corrected_match.strip())
            else:
                measurements.append(match.strip())
    return s, measurements

def extract_dimensions(s: str) -> List[str]:
    if not s or s in ['nan', '']:
        return []
    dimension_measurements: List[str] = []
    for unit in units:
        matches: List[str] = re.findall(rf'{number_pattern}{unit} ?{dimension_symbol_pattern} ?{number_pattern}{unit}', s)
        dimension_measurements.extend(matches)
    return dimension_measurements




# TODO: fix/change params to allow use of .apply()
def extract_name_from_address(row: Series, address_col: str):
    customer: str = row['Customer']
    address: str = row[address_col]
    
    # Remove the customer name from the beginning of the address
    if address.startswith(customer):
        address = address[len(customer):].strip()
    
    # Remove common prefixes like "Attn:"
    if address.startswith('Attn:'):
        address = address[len('Attn:'):].strip()
    
    # Extract the name part from the remaining address by removing titles and addresses
    # Assume names are usually in the form "Firstname Lastname" or "Firstname Lastname, Title"
    match = re.search(r'([A-Za-z]+ [A-Za-z]+)', address)
    if match:
        person_name = match.group(1)
        return person_name 
    return customer


# TODO: some redundancy with split_name..
def trim_name(name):
    # Check if the input is a string; if not, return None values
    if not isinstance(name, str):
        return Series([None, None])
    # Titles like "Dr." at the start and suffixes like "NP", "RN" at the end are removed
    match = re.match(r'(?:Dr\.\s*)?([A-Za-z]+)\s+([A-Za-z]+)(?:\s+[A-Z\-]{2,4})?$', name)
    if match:
        first_name = match.group(1)
        last_name = match.group(2)
        return Series([first_name, last_name])
    return Series([None, None])  # Handle case where regex does not match


# df[a, b] = df[name_col].apply(split_name)
def split_name(fullname: str):
    # Goal: name -> Series[First, Last, JobTitle]
    # 1: Remove "Attn: "
    # 2: Store then remove titles
    # 3: Separate into First and Last
    suffix_pattern = re.compile(r'(,?\s*(' + name_suffixes + r'))$', re.IGNORECASE)
    prefix_pattern = re.compile(r'\bDr\.*\s+', re.IGNORECASE)
    if not fullname or not isinstance(fullname, str):
        return Series(['', '', ''])

    if fullname.startswith('Attn:'):
        fullname = fullname[len('Attn:'):].strip()

    fullname = prefix_pattern.sub('', fullname).strip()

    # Extract and remove suffixes (titles) from the end of the name
    job_title = ''
    suffix_match = suffix_pattern.search(fullname)
    if suffix_match:
        job_title = suffix_match.group(1).strip(', ').upper()
        fullname = suffix_pattern.sub('', fullname).strip()

    name_parts = fullname.split()
    first, last = name_parts[0], ''
    
    if len(name_parts) > 1:
        last = ' '.join(name_parts[1:])
    
    return Series([first, last, job_title])


country_patterns = re.compile(r'\b(United States|USA)\b', re.IGNORECASE)
# TODO: make separate method to return address as PD series; return tuple in original one
def parse_address(address: str):
    if not isinstance(address, str):
        return Series(['', '', '', '', ''])
    address = country_patterns.sub('', address)
    address, phone_number = extract_phone(text=address)
    address, zip_code = extract_zip(text=address)
    address, state = extract_state(text=address)
    address, city = extract_city(text=address)
    return Series([address, city, state, zip_code, phone_number])

def extract_phone(text: str) -> Tuple[str, str | None]:
    if not isinstance(text, str):
        return text, ''
    phone_pattern = re.compile(
        r'''
        (\+?1[-.\s]?|\()?  # Optional country code (+1) with optional space, dash, or dot, or opening parenthesis
        (\d{3})[-.\s)]*    # Area code with optional closing parenthesis, space, dash, or dot
        (\d{3})[-.\s]*     # First three digits with optional space, dash, or dot
        (\d{4})            # Last four digits
        ''', 
        re.VERBOSE
    )
    phone_match = phone_pattern.search(text)
    # Extract the phone number if present and format it as 999-999-9999
    if phone_match:
        phone_number = f"{phone_match.group(2)}-{phone_match.group(3)}-{phone_match.group(4)}"
    else:
        phone_number = None
    text = phone_pattern.sub('', text).strip()
    return text, phone_number

def extract_zip(text: str)  -> Tuple[str, str | None]:
    zip_code_pattern = re.compile(
        r'(\d{5})(-\d{4})?\b'  # Match 5 digits optionally followed by a hyphen and 4 more digits
    )
    zip_code_match = zip_code_pattern.search(text)
    zip_code = zip_code_match.group() if zip_code_match else None
    text = zip_code_pattern.sub('', text).strip()
    return text, zip_code    

def extract_state(text: str) -> Tuple[str, str | None]:
    states_pattern = re.compile(
        r'\b(' + '|'.join(STATE_ABBREVIATIONS + STATE_NAMES) + r')\b',
        re.IGNORECASE
    )
    # Find all matches of state abbreviations/full names
    matches = list(states_pattern.finditer(text))
    # Determine the last match (rightmost state) //recall case when street_suffix = Ct
    last_match = matches[-1] if matches else None
    # Extract state and update text
    state = last_match.group(1) if last_match else None
    if last_match:
        # Remove only the last match from the text
        start, end = last_match.span()
        text = text[:start].rstrip() + text[end:].lstrip()
    
    return text, state

def extract_city(text: str, cities: Optional[List[str]] = None) -> Tuple[str, Optional[str]]:
    known_cities_pattern = '|'.join([re.escape(city) for city in cities]) if cities else ''
    city = None
    # First, look for suite/unit patterns to determine where the city might start
    suite_match = re.search(suite_pattern, text, re.IGNORECASE)
    if suite_match:
        city_start_idx = suite_match.end()
        city = text[city_start_idx:].strip('., ').split(',')[0].strip()
    else:
        # If no suite/unit pattern, look for a street suffix
        street_match = re.search(street_suffix_pattern, text)
        if street_match:
            street_end_idx = street_match.end()
            # Assume city follows immediately after the street suffix
            potential_city = text[street_end_idx:].strip('., ').split(',')[0].strip()
            if potential_city and potential_city.split()[0] not in street_suffix_list:
                city = potential_city
        
        # Fallback if no suite or street suffix is found
        if not city:
            parts = text.split(',')
            if len(parts) > 1:
                city = parts[-2].strip('. ')

    # If there's a list of known cities, refine the city match using it   
    if city and known_cities_pattern:
        city_match = re.search(r'\b(' + known_cities_pattern + r')\b', city, re.IGNORECASE)
        if city_match:
            city = city_match.group(1)

    # Clean up the city name from unnecessary characters
    if city:
        text = re.sub(re.escape(city), '', text).strip(', ')
    return text, city

STATE_ABBREVIATIONS: List[str] = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
    "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
    "VA", "WA", "WV", "WI", "WY"
]
STATE_NAMES: List[str] = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
    "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
    "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
    "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
]
street_suffix_pattern = r'\b(?:Rd|Road|St|Street|Ave|Avenue|Blvd|Boulevard|Ln|Lane|Dr|Drive|Ct|Court|Pl|Place|Sq|Square|Terrace|Hwy|Pkwy|Parkway|Cir|Circle|Way|Ste|Suite|(PO Box[\s#]*\d+))\.*\b'
street_suffix_list = ['Rd', 'Road', 'St', 'Street', 'Ave', 'Avenue', 'Blvd', 'Boulevard', 'Ln', 'Lane', 'Dr', 'Drive', 'Ct', 'Court', 'Pl', 'Place', 'Sq', 'Square', 'Terrace', 'Hwy', 'Pkwy', 'Parkway', 'Cir', 'Circle', 'Way', 'Ste', 'Suite', 'PO Box']  #'|'.join
suite_pattern = r'(Suite|Ste|Unit|#)\s*[A-Z\d]+'

units: List[str] = [
    'units', 'oz', 'g', 'ml', 'fl oz', 'lb', 'kg', 'gal', 'cc'
]
number_pattern: str = r'\d+\.?\d*'
dimension_symbol_pattern: str = r'[xX/]'
name_suffixes = r'MSPA|BSN|FNP-C|LME|DOO|PA-C|MSN-RN|RN|NP|CRNA|FNP|PA|NMD|MD|DO|LE|CMA|OM'
