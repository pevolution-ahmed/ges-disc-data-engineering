
from pkg_resources import SOURCE_DIST


class Extractor:
    """
        Extractor class is a class that extract data from multiple sources
        based on the type of the source that will extract data from
    
    """
    DATA_SOURCES = ["API","CSV","JSON","DB"]
    def __init__(source_type: str,dest: str,self) -> self:
        pass