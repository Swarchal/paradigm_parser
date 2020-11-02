"""
Parse Paradigm files
"""


class ParsingError(Exception):
    """Custom error class"""
    pass


class Plate:
    """Plate class within a Paradigm file"""

    def __init__(self, data_sublist):
        data_sublist = list(filter(None, data_sublist))
        if len(data_sublist) != 4:
            raise ParsingError
        if data_sublist[-1] != "~End":
            raise ParsingError
        if not data_sublist[0].startswith("Plate"):
            raise ParsingError
        self.data_sublist = data_sublist

    def __str__(self):
        return self.plate_name

    def __repr__(self):
        return f"Plate object <{self.plate_name}>"

    @property
    def plate_name(self):
        return self.data_sublist[0].split("\t")[1]

    @property
    def temperature(self):
        return int(self.data_sublist[2].split("\t")[0])

    @property
    def n_wells(self):
        return int(self.data_sublist[0].split("\t")[18])

    @property
    def wells(self):
        return self.data_sublist[1].split("\t")[1:]

    @property
    def values(self):
        value_strs = self.data_sublist[2].split("\t")[1:]
        return [float(i) for i in value_strs]

    def parse(self):
        return {well: value for well, value in zip(self.wells, self.values)}



class Paradigm:
    """Paradigm file class"""

    def __init__(self, filepath, encoding="latin-1"):
        self.filepath = filepath
        self.data_list = self.open_file(encoding)
        self.plate_list = self.split_into_plates()
        self.plate_store = {}
        self.plates = []
        # TODO try and handle encoding errors automatically by trying
        # different encodings on ParsingErrors
        for index, plate_sub_list in enumerate(self.plate_list):
            plate = Plate(plate_sub_list)
            self.plate_store[plate.plate_name] = plate
            self.plates.append(plate.plate_name)

    def __len__(self):
        return len(self.plates)

    def __getitem__(self, name):
        return self.plate_store[name].parse()

    def open_file(self, encoding):
        """open file to list, line per item"""
        with open(self.filepath, "r", encoding=encoding) as f:
            data = [i.strip() for i in f.readlines()]
        return data

    @property
    def n_blocks(self):
        """get number of blocks from data list"""
        block_str = self.data_list[0]
        if not block_str.startswith("##"):
            err_msg = f"Expected file to start with '##BLOCKS', but got: '{block_str}'"
            raise RuntimeError(err_msg)
        return int(block_str.strip().split("=")[-1])

    @property
    def n_plates(self):
        return len(self.plates)

    def split_into_plates(self):
        """split data_list into sub-lists for each plate"""
        return list(chunks(self.data_list[1:-1], 5))


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

