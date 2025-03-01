"""Testing of File Renaming."""
import json
import os
import pathlib
import shutil
import tempfile
from typing import Any, DefaultDict

import click
import pytest
from typer.testing import CliRunner

from polus.plugins.formats.file_renaming import file_renaming as fr
from polus.plugins.formats.file_renaming.__main__ import app as app

runner = CliRunner()


class CreateData:
    """Generate tabular data with several different file format."""

    def __init__(self):
        """Define instance attributes."""
        self.dirpath = pathlib.Path(__file__).parent
        self.jsonpath = self.dirpath.joinpath("file_rename_test.json")

    def input_directory(self) -> pathlib.Path:
        """Create temporary input directory."""
        return tempfile.mkdtemp(dir=self.dirpath)

    def sub_directory(self) -> pathlib.Path:
        """Create temporary input directory."""
        dir_path = self.input_directory()
        flist = [
            "taoe005-u2os-72h-cp-a-au00044859_a01_s3_w23db644df-02ee-429d-9559-09cf4625c62b.tif",
            "taoe005-u2os-72h-cp-a-au00044859_b01_s3_w3add254c8-0c7b-4cf0-a5dc-bf0cf8de8cec.tif",
            "taoe005-u2os-72h-cp-a-au00044859_b07_s5_w2da098211-f7c1-453d-954f-b7d4751f6daa.tif",
            "taoe005-u2os-72h-cp-a-au00044859_c15_s2_w3aea523fa-3b89-46a7-95e3-604017151895.tif",
        ]
        for i in range(5):
            dirname = pathlib.Path(dir_path, f"folder_{i}")
            if not pathlib.Path(dirname).exists():
                pathlib.Path(dirname).mkdir(exist_ok=False, parents=False)
            for fl in flist:
                temp_file = open(pathlib.Path(dirname, fl), "w")
                temp_file.close()

        return pathlib.Path(dir_path)

    def output_directory(self) -> pathlib.Path:
        """Create temporary output directory."""
        return tempfile.mkdtemp(dir=self.dirpath)

    def runcommands(self, inputs, inp_pattern, out_pattern) -> click.testing.Result:
        """Run command line arguments."""
        inp_dir = self.input_directory()
        out_dir = self.output_directory()
        for inp in inputs:
            open(pathlib.Path(inp_dir, inp), "w").close()

        outputs = runner.invoke(
            app,
            [
                "--inpDir",
                str(inp_dir),
                "--filePattern",
                inp_pattern,
                "--outDir",
                str(out_dir),
                "--outFilePattern",
                out_pattern,
            ],
        )
        return outputs

    def load_json(self, x) -> DefaultDict[Any, Any]:
        """Json file containing image filenames."""
        with open(self.jsonpath) as file:
            data = json.load(file)
        return data[x]

    def clean_directories(self) -> None:
        """Remove files."""
        for d in self.dirpath.iterdir():
            if d.is_dir() and d.name.startswith("tmp"):
                shutil.rmtree(d)


fixture_params = [
    [
        (
            "r{row:ddd}_c{col:ddd}_{chan:ccc}.ome.tif",
            "output_r{row:dddd}_c{col:dddd}_{chan:d+}.ome.tif",
        ),
        (
            "r{row:d+}_c{col:d+}_{chan:c+}.ome.tif",
            "output_r{row:dddd}_c{col:dddd}_{chan:d+}.ome.tif",
        ),
        ("r.ome.tif", "output_r{row:dddd}_c{col:dddd}_{chan:d+}.ome.tif"),
        (
            "%{row:ddd}_c{col:ddd}_z{z:d+}.ome.tif",
            "%{row:dddd}_col{col:dddd}_z{z:d+}.ome.tif",
        ),
        (
            "00{one:d}0{two:dd}-{three:d}-00100100{four:d}.tif",
            "output{one:dd}0{two:ddd}-{three:dd}-00100100{four:dd}.tif",
        ),
        (
            "S1_R{one:d}_C1-C11_A1_y0{two:dd}_x0{three:dd}_c0{four:dd}.ome.tif",
            "output{one:dd}_C1-C11_A1_y0{two:ddd}_x0{three:ddd}_c0{four:ddd}.ome.tif",
        ),
        (
            "S1_R{one:d}_C1-C11_A1_y{two:d+}_x{three:d+}_c{four:d+}.ome.tif",
            "output{one:dd}_C1-C11_A1_y{two:d+}_x{three:d+}_c{four:d+}.ome.tif",
        ),
        (
            "img_x{row:dd}_y{col:dd}_({chan:c+}).tif",
            "output{row:dd}_{col:ddd}_{chan:dd}.tif",
        ),
        (
            "img_x{row:dd}_y{col:dd}_{chan:c+}_{ychan:c+}.tif",
            "output{row:ddd}_{col:ddd}_{chan:dd}_{ychan:ddd}.tif",
        ),
        (
            "img_x{row:dd}_y{col:dd}_{chan:c+}_{ychan:c+}_{alphachan:ccc}.tif",
            "output{row:ddd}_{col:ddd}_{chan:dd}_{ychan:ddd}_{alphachan:dddd}.tif",
        ),
        (
            "img x{row:dd} y{col:dd} {chan:ccc}.tif",
            "output{row:ddd}_{col:ddd}_{chan:ccc}.tif",
        ),
        (
            "p{p:d}_y{y:d}_r{r:d+}_c{c:d+}.ome.tif",
            "p{p:dd}_y{y:dd}_r{r:dddd}_c{c:ddd}.ome.tif",
        ),
        (
            "img x{row:dd} y{col:dd} {chan:c+}.tif",
            "output{row:ddd}_{col:ddd}_{chan:dd}.tif",
        ),
        (
            "img x{row:dd}.{other:d+} y{col:dd} {chan:c+}.tif",
            "output{row:ddd}_{col:ddd}_ {other:d+} {chan:dd}.tif",
        ),
        (
            "0({mo:dd}-{day:dd})0({mo2:dd}-{day2:dd})-({a:d}-{b:d})-{col:ddd}.ome.tif",
            "0({mo:ddd}-{day:ddd})0{mo2:dd}-{day2:dd})-({a:dd}-{b:dd})-{col:ddd}.ome.tif",
        ),
    ]
]


@pytest.fixture(params=fixture_params)
def poly(request):
    """To get the parameter of the fixture."""
    return request.param


def test_duplicate_channels_to_digit(poly):
    """Testing of duplicate channels to digits."""
    d = CreateData()
    inputs = d.load_json("duplicate_channels_to_digit")
    (inp_pattern, out_pattern) = poly[0]
    outputs = d.runcommands(inputs, inp_pattern, out_pattern)
    assert outputs.exit_code == 0


def test_duplicate_channels_to_digit_non_spec_digit_len(poly):
    """Testing of duplicate channels to digits with non specified length of digits."""
    d = CreateData()
    inputs = d.load_json("duplicate_channels_to_digit")
    (inp_pattern, out_pattern) = poly[1]
    outputs = d.runcommands(inputs, inp_pattern, out_pattern)
    assert outputs.exit_code == 0


def test_invalid_input_raises_error(poly):
    """Testing of invalid input filepattern."""
    d = CreateData()
    inputs = d.load_json("duplicate_channels_to_digit")
    (inp_pattern, out_pattern) = poly[0]
    d.runcommands(inputs, inp_pattern, out_pattern)


def test_non_alphanum_inputs_percentage_sign(poly):
    """Testing of filename with non alphanumeric inputs such as percentage sign."""
    d = CreateData()
    inputs = d.load_json("percentage_file")
    (inp_pattern, out_pattern) = poly[3]
    outputs = d.runcommands(inputs, inp_pattern, out_pattern)
    assert outputs.exit_code == 0


def test_numeric_fixed_width(poly):
    """Testing of filename with numeric fixed length."""
    d = CreateData()
    inputs = d.load_json("robot")
    (inp_pattern, out_pattern) = poly[4]
    outputs = d.runcommands(inputs, inp_pattern, out_pattern)
    assert outputs.exit_code == 0


def test_alphanumeric_fixed_width(poly):
    """Testing of filename with alphanumeric fixed length."""
    d = CreateData()
    inputs = d.load_json("brain")
    (inp_pattern, out_pattern) = poly[5]
    outputs = d.runcommands(inputs, inp_pattern, out_pattern)
    assert outputs.exit_code == 0


def test_alphanumeric_variable_width(poly):
    """Testing of filename with alphanumeric variable width."""
    d = CreateData()
    inputs = d.load_json("variable")
    (inp_pattern, out_pattern) = poly[6]
    outputs = d.runcommands(inputs, inp_pattern, out_pattern)
    assert outputs.exit_code == 0
    d.clean_directories()


def test_parenthesis(poly):
    """Testing of filename with parenthesis."""
    d = CreateData()
    inputs = d.load_json("parenthesis")
    (inp_pattern, out_pattern) = poly[7]
    outputs = d.runcommands(inputs, inp_pattern, out_pattern)
    assert outputs.exit_code == 0


def test_two_chan_to_digit(poly):
    """Testing conversion of two channels to digits."""
    d = CreateData()
    inputs = d.load_json("two_chan")
    (inp_pattern, out_pattern) = poly[8]
    outputs = d.runcommands(inputs, inp_pattern, out_pattern)
    assert outputs.exit_code == 0


def test_three_chan_to_digit(poly):
    """Test conversion of three channels to digits."""
    d = CreateData()
    inputs = d.load_json("three_chan")
    (inp_pattern, out_pattern) = poly[9]
    outputs = d.runcommands(inputs, inp_pattern, out_pattern)
    assert outputs.exit_code == 0


def test_three_char_chan(poly):
    """Test conversion of three character channels to digits."""
    d = CreateData()
    inputs = d.load_json("three_char_chan")
    (inp_pattern, out_pattern) = poly[10]
    outputs = d.runcommands(inputs, inp_pattern, out_pattern)
    assert outputs.exit_code == 0


def test_varied_digits(poly):
    """Test varied digits."""
    d = CreateData()
    inputs = d.load_json("tissuenet-val-labels-45-C")
    (inp_pattern, out_pattern) = poly[11]
    outputs = d.runcommands(inputs, inp_pattern, out_pattern)
    assert outputs.exit_code == 0
    d.clean_directories()


def test_spaces(poly):
    """Test non-alphanumeric chars such as spaces."""
    d = CreateData()
    inputs = d.load_json("non_alphanum_int")
    (inp_pattern, out_pattern) = poly[12]
    outputs = d.runcommands(inputs, inp_pattern, out_pattern)
    assert outputs.exit_code == 0


def test_non_alphanum_float(poly):
    """Test non-alphanumeric chars such as spaces, periods, commas, brackets."""
    d = CreateData()
    inputs = d.load_json("non_alphanum_float")
    (inp_pattern, out_pattern) = poly[13]
    outputs = d.runcommands(inputs, inp_pattern, out_pattern)
    assert outputs.exit_code == 0
    d.clean_directories()


def test_dashes_parentheses(poly):
    """Test non-alphanumeric chars are handled properly such as dashes, parenthesis."""
    d = CreateData()
    inputs = d.load_json("kph-kirill")
    (inp_pattern, out_pattern) = poly[14]
    outputs = d.runcommands(inputs, inp_pattern, out_pattern)
    assert outputs.exit_code == 0
    d.clean_directories()


def test_map_pattern_grps_to_regex_valid_input():
    """Test of mapping input pattern."""
    test_cases = [
        (
            ("img_x{row:dd}_y{col:dd}_{channel:c+}.tif"),
            (
                {
                    "row": "(?P<row>[0-9][0-9])",
                    "col": "(?P<col>[0-9][0-9])",
                    "channel": "(?P<channel>[a-zA-Z]+)",
                }
            ),
        ),
        (("img_x{row:c+}.tif"), ({"row": "(?P<row>[a-zA-Z]+)"})),
        ((""), ({})),
    ]
    for test_case in test_cases:
        (from_val, to_val) = test_case
        result = fr.map_pattern_grps_to_regex(from_val)
        assert result == to_val


def test_convert_to_regex_valid_input():
    """Test of converting to regular expression pattern."""
    test_cases = [
        (
            ("img_x{row:dd}_y{col:dd}_{channel:c+}.tif"),
            (
                {
                    "row": "(?P<row>[0-9][0-9])",
                    "col": "(?P<col>[0-9][0-9])",
                    "channel": "(?P<channel>[a-zA-Z]+)",
                }
            ),
            (
                "img_x(?P<row>[0-9][0-9])_y(?P<col>[0-9][0-9])_(?P<channel>[a-zA-Z]+).tif"
            ),
        ),
        (
            ("img_x{row:c+}.tif"),
            ({"row": "(?P<row>[a-zA-Z]+)"}),
            ("img_x(?P<row>[a-zA-Z]+).tif"),
        ),
        (("img_x01.tif"), ({}), ("img_x01.tif")),
    ]
    for test_case in test_cases:
        (from_val1, from_val2, to_val) = test_case
        result = fr.convert_to_regex(from_val1, from_val2)
        assert result == to_val


def test_specify_len_valid_input():
    """Test of sepcifying length."""
    test_cases = [
        (
            ("newdata_x{row:ddd}_y{col:ddd}_c{channel:ddd}.tif"),
            ("newdata_x{row:03d}_y{col:03d}_c{channel:03d}.tif"),
        ),
        (("newdata_x{row:c+}.tif"), ("newdata_x{row:s}.tif")),
        (("newdata_x01.tif"), ("newdata_x01.tif")),
    ]
    for test_case in test_cases:
        (from_val, to_val) = test_case
        result = fr.specify_len(from_val)
        assert result == to_val


def test_get_char_to_digit_grps_returns_unique_keys_valid_input():
    """Test of getting characters to digit groups."""
    test_cases = [
        (
            ("img_x{row:dd}_y{col:dd}_{channel:c+}.tif"),
            ("newdata_x{row:ddd}_y{col:ddd}_c{channel:ddd}.tif"),
            (["channel"]),
        ),
        (("img_x{row:c+}.tif"), ("newdata_x{row:c+}.tif"), ([])),
        (("img_x01.tif"), ("newdata_x01.tif"), ([])),
    ]
    for test_case in test_cases:
        (from_val1, from_val2, to_val) = test_case
        result = fr.get_char_to_digit_grps(from_val1, from_val2)
        assert result == to_val


def test_extract_named_grp_matches_valid_input():
    """Test of extracting group names."""
    test_cases = [
        (
            (
                "img_x(?P<row>[0-9][0-9])_y(?P<col>[0-9][0-9])_(?P<channel>[a-zA-Z]+).tif"
            ),
            (["img_x01_y01_DAPI.tif", "img_x01_y01_GFP.tif", "img_x01_y01_TXRED.tif"]),
            (
                [
                    {
                        "row": "01",
                        "col": "01",
                        "channel": "DAPI",
                        "fname": "img_x01_y01_DAPI.tif",
                    },
                    {
                        "row": "01",
                        "col": "01",
                        "channel": "GFP",
                        "fname": "img_x01_y01_GFP.tif",
                    },
                    {
                        "row": "01",
                        "col": "01",
                        "channel": "TXRED",
                        "fname": "img_x01_y01_TXRED.tif",
                    },
                ]
            ),
        ),
        (("img_x01.tif"), (["img_x01.tif"]), ([{"fname": "img_x01.tif"}])),
    ]
    for test_case in test_cases:
        (from_val1, from_val2, to_val) = test_case
        result = fr.extract_named_grp_matches(from_val1, from_val2)
        assert result == to_val


def test_extract_named_grp_matches_bad_pattern_invalid_input_fails():
    """Test of invalid input pattern."""
    test_cases = [
        (
            ("img_x(?P<row>[a-zA-Z]+).tif"),
            (["img_x01_y01_DAPI.tif", "img_x01_y01_GFP.tif", "img_x01_y01_TXRED.tif"]),
        )
    ]
    for test_case in test_cases:
        (from_val1, from_val2) = test_case

        result = fr.extract_named_grp_matches(from_val1, from_val2)
        assert len(result) == 0


def test_str_to_int_valid_input():
    """Test of string to integer."""
    test_cases = [
        (
            (
                {
                    "row": "01",
                    "col": "01",
                    "channel": "DAPI",
                    "fname": "img_x01_y01_DAPI.tif",
                }
            ),
            ({"row": 1, "col": 1, "channel": "DAPI", "fname": "img_x01_y01_DAPI.tif"}),
        ),
        (
            (
                {
                    "row": "2",
                    "col": "01",
                    "channel": "TXRED",
                    "fname": "img_x01_y01_TXRED.tif",
                }
            ),
            (
                {
                    "row": 2,
                    "col": 1,
                    "channel": "TXRED",
                    "fname": "img_x01_y01_TXRED.tif",
                }
            ),
        ),
        (
            (
                {
                    "row": "0001",
                    "col": "0001",
                    "channel": "GFP",
                    "fname": "img_x01_y01_GFP.tif",
                }
            ),
            ({"row": 1, "col": 1, "channel": "GFP", "fname": "img_x01_y01_GFP.tif"}),
        ),
    ]
    for test_case in test_cases:
        (from_val, to_val) = test_case
        result = fr.str_to_int(from_val)
        assert result == to_val


def test_letters_to_int_returns_cat_index_dict_valid_input():
    """Test of letter to integers."""
    test_cases = [
        (
            ("channel"),
            [
                {
                    "row": 1,
                    "col": 1,
                    "channel": "DAPI",
                    "fname": "img_x01_y01_DAPI.tif",
                },
                {"row": 1, "col": 1, "channel": "GFP", "fname": "img_x01_y01_GFP.tif"},
                {
                    "row": 1,
                    "col": 1,
                    "channel": "TXRED",
                    "fname": "img_x01_y01_TXRED.tif",
                },
            ],
            ({"DAPI": 0, "GFP": 1, "TXRED": 2}),
        )
    ]
    for test_case in test_cases:
        (from_val1, from_val2, to_val) = test_case
        result = fr.letters_to_int(from_val1, from_val2)
        assert result == to_val


@pytest.mark.xfail
def test_extract_named_grp_matches_duplicate_namedgrp_invalid_input():
    """Test of invalid input pattern."""
    test_cases = [
        (
            (
                "x(?P<row>[0-9][0-9])_y(?P<row>[0-9][0-9])_c(?P<channel>[a-zA-Z]+).ome.tif"
            ),
            (["img_x01_y01_DAPI.tif", "img_x01_y01_GFP.tif", "img_x01_y01_TXRED.tif"]),
        )
    ]
    for test_case in test_cases:
        (from_val1, from_val2) = test_case
        fr.extract_named_grp_matches(from_val1, from_val2)


@pytest.mark.xfail
def test_letters_to_int_returns_error_invalid_input():
    """Test of invalid inputs."""
    test_cases = [
        (
            (2),
            [
                {
                    "row": 1,
                    "col": 1,
                    "channel": "DAPI",
                    "fname": "img_x01_y01_DAPI.tif",
                },
                {"row": 1, "col": 1, "channel": "GFP", "fname": "img_x01_y01_GFP.tif"},
                {
                    "row": 1,
                    "col": 1,
                    "channel": "TXRED",
                    "fname": "img_x01_y01_TXRED.tif",
                },
            ],
        ),
    ]
    for test_case in test_cases:
        (from_val1, from_val2) = test_case
        fr.letters_to_int(from_val1, from_val2)


def test_cli() -> None:
    """Test Cli."""
    for i in ["raw", "map", ""]:
        d = CreateData()
        inpdir = d.sub_directory()
        if i == "":
            inp_dir = pathlib.Path(inpdir, "folder_0")
        else:
            inp_dir = inpdir
        out_dir = d.output_directory()
        file_pattern = ".*_{row:c}{col:dd}_s{s:d}_w{channel:d}.*.tif"
        out_file_pattern = "x{row:dd}_y{col:dd}_p{s:dd}_c{channel:d}.tif"
        result = runner.invoke(
            app,
            [
                "--inpDir",
                inp_dir,
                "--filePattern",
                file_pattern,
                "--outDir",
                out_dir,
                "--outFilePattern",
                out_file_pattern,
                "--mapDirectory",
                i,
            ],
        )
        assert result.exit_code == 0
        if i == "raw":
            outfile = [f for f in os.listdir(out_dir) if "folder" in f]
            assert len(outfile) == 20
        elif i == "map":
            outfile = [f for f in os.listdir(out_dir) if "d" in f]
            assert len(outfile) == 20
        else:
            outfile = [f for f in os.listdir(out_dir) if not f.startswith("folder|d")]
            assert len(outfile) == 4

        d.clean_directories()
