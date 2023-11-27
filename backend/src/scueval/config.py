from dataclasses import dataclass

from scueval.structs import Bounds


@dataclass
class SearchParams:
    header_search_bounds = Bounds(None, 650, None, 770)     # The boundaries to search for the header textbox
    minimum_header_len: int = 80                            # The minimum length of the header textbox

    item_id_bounds = Bounds(25, None, 43, None)             # The x-bounds for an item's ID
    item_description_bounds = Bounds(44, None, 250, None)   # The x-bounds for an item's Question Description
    item_data_bounds = Bounds(330, None, 460, None)         # The x-bounds for an item's raw data percentage
    item_summary_bounds = Bounds(540, None, 590, None)      # The x=bounds for an item's summary data

