# bidsconv

Like putting your fMRI data into [BIDS](https://bids.neuroimaging.io/) format? Like using [`dcm2bids`](https://cbedetti.github.io/Dcm2Bids/) to do so? Too lazy to use a for-loop to iterate through each subject and call `dcm2bids`? If you're like me and answered yes to all of the above, then `bidsconv` is for you!

Bidsconv is a multi-subject wrapper for `dcm2bids`, which lets you easily convert full data sets into BIDS format. Nothing special to it other than looping over multiple subject and session directories! `bidsconv` will also create your `participants.tsv` file, as well as blank `README`, `CHANGES` and `dataset_description.json` files.  

To install:

You must have `dcm2bids` installed first. To install `dcm2bids`:

`pip install dcm2bids`

Then, install `bidsconv`:

```
git clone git@github.com:danjgale/bidsconv.git
cd bidsconv/
pip install -e .
```

To run:

`bidsconv -d your-dicom-directory -o your-bids-directory -c your-bids-config-file.json`

Where `your-dicom-directory` is a directory that has one sub-directory per subject, and `your-bids-directory` is your empty BIDS directory that you wish to create.  

`your-bids-config-file.json` is the configuration file, and follows the exact same format as the one used by `dcm2bids` (see example [here](https://github.com/cbedetti/Dcm2Bids/blob/master/example/config.json)). Refer to `dcm2bids` for documentation.

If you have multiple sessions, you'll need to call `bidsconv` for each session:

`bidsconv -d your-dicom-directory-ses-01 -o your-bids-directory -c your-bids-config-file.json -s ses-01`
`bidsconv -d your-dicom-directory-ses-02 -o your-bids-directory -c your-bids-config-file.json -s ses-02`

The full CLI can be shown by calling `bidsconv -h`:

```
usage: bidsconv [-h] [-d dicom_dir] [-o output_dir]
               [--ignore ignored_dirs [ignored_dirs ...]] [-s session]
               [-c config] [--force-run-labels] [-m mapping]

optional arguments:
  -h, --help            show this help message and exit
  -d dicom_dir          The path to the directory which contains all subjects'
                        dicom images.
  -o output_dir         The path to the directory which contains all subjects'
                        BIDS data.
  --ignore ignored_dirs [ignored_dirs ...]
                        Subdirectories in `-d` to ignore.
  -s session            Session number, e.g., 'ses-01'
  -c config             Configuration .json file for dcm2bids. Refer to
                        dcm2bids documentation for examples.
  --force-run-labels    Force all functional runs to have a run number. This
                        means that singleton runs, i.e. tasks that have only
                        one functional run will be labeled as `run-01`. This
                        is a necessary workaround for fmriprep 1.4.0 or
                        greater. Otherwise, singleton runs will not have a run
                        number/label, which is the default for dcm2bids.
  -m mapping            .json file containing specific mappings between input
                        dicom folders (keys) and subject IDs (values). Useful
                        for multi-session data in which different dicom
                        folders belong to the same subject.

```

**Note:** This package was developed for the [Memory, Action, and Perception](http://www.gallivanmaplab.com/home) lab here at Queen's University, and works for us quite well. That said, it's not a fully-tested one-size-fits-all tool for your BIDS conversions. And it's definitely in its early stages. So, if you run into any problems please let us know by creating an issue on Github. If it's *really* not working, then using `dcm2bids` directly is probably much easier!