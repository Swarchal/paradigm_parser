"""
Parse Paradigm files
"""


class Plate:
    """Plate class within a Paradigm file"""

    def __init__(self, data_sublist):
        data_sublist = list(filter(None, data_sublist))
        assert len(data_sublist) == 4, print(data_sublist)
        assert data_sublist[-1] == "~End"
        assert data_sublist[0].startswith("Plate")
        self.data_sublist = data_sublist

    def __str__(self):
        return self.plate_name

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
        self.encoding = encoding
        self.data_list = self.open_file()
        self.plate_list = self.split_into_plates()
        self.plates = {}
        for plate_sub_list in self.plate_list:
            plate = Plate(plate_sub_list)
            self.plates[plate.plate_name] = plate

    def __len__(self):
        return len(self.plates)

    def __getitem__(self, index):
        return list(self.plates.values())[index]

    def open_file(self):
        """open file to list, line per item"""
        with open(self.filepath, "r", encoding=self.encoding) as f:
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

