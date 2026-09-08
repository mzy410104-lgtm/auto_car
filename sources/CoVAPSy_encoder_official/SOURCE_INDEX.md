# Official CoVAPSy Sources for the Speed-Sensing Mechanical Parts

> Git archive note: this repository tracks the source index. The manufacturer PDF/CAD copies listed below remain local and are not published through Git. Other members can obtain the files from the original sources in the tables and check them against these records.

Archive date: 2026-09-08 (local time in France). The current design uses 1 OPTEK OPB815WZ, following the official perforated transmission gear and dedicated gear cover for mounting the photointerrupter. This directory stores only the original reference materials; no modifications, format conversions, or manufacturing drawings have been produced.

## Original Mechanical Files

The directory was checked through the [official repository page](https://github.com/ajuton-ens/CourseVoituresAutonomesSaclay/tree/main/Hardware/pieces_mecaniques_stp_dxf) and the [GitHub directory API](https://api.github.com/repos/ajuton-ens/CourseVoituresAutonomesSaclay/contents/Hardware/pieces_mecaniques_stp_dxf). The download addresses below were taken directly from the returned `download_url` values, and the filenames are unchanged.

| File | Download date | Size in bytes | Original download address |
|---|---|---:|---|
| `Carter pignon support fourche.stp` | 2026-09-08 | 679821 | [Official original STP](https://raw.githubusercontent.com/ajuton-ens/CourseVoituresAutonomesSaclay/main/Hardware/pieces_mecaniques_stp_dxf/Carter%20pignon%20support%20fourche.stp) |
| `Pignon intermediaire 70dts.dxf` | 2026-09-08 | 311368 | [Official original DXF](https://raw.githubusercontent.com/ajuton-ens/CourseVoituresAutonomesSaclay/main/Hardware/pieces_mecaniques_stp_dxf/Pignon%20intermediaire%2070dts.dxf) |

After downloading, the byte counts were checked and SHA-1 hashes were calculated using Git blob rules. They matched the official API values:

- `Carter pignon support fourche.stp`: `759dee53fa9a70020e5d86cf4b74f152f3568b81`
- `Pignon intermediaire 70dts.dxf`: `38b8328561d60877b978f7866b233528f22aa755`

## Copies of Assembly References

The following files were copied from this project's `tmp/pdfs/covapsy_encoder_mount/` directory into the archive on 2026-09-08. Each copy was confirmed to be byte-for-byte identical to its original; the originals were not deleted. The PDFs were not downloaded again during this operation.

| File | Size in bytes | Original source URL | Relevant content reviewed |
|---|---:|---|---|
| `Guide_Assemblage_kit_CoVAPSy.pdf` | 2956991 | [Original PDF (pinned commit)](https://raw.githubusercontent.com/ajuton-ens/CourseVoituresAutonomesSaclay/079841a5aa8e59d97413295f268a9689767dbdb5/Hardware/Guide_Assemblage_kit_CoVAPSy.pdf) | Page 5: photointerrupter mounting position, using 2 MB1 or MA2 screws; page 6: connection diagram |
| `Photos_kit_CoVAPSy_2024.pdf` | 5685712 | [Original PDF (pinned commit)](https://raw.githubusercontent.com/ajuton-ens/CourseVoituresAutonomesSaclay/079841a5aa8e59d97413295f268a9689767dbdb5/Hardware/Photos_kit_CoVAPSy_2024.pdf) | Page 2: item 23, perforated speed-sensing gear; item 24, photointerrupter mounting cover; item 15, photointerrupter |

## Scope of the Checks and Limits on Use

- The official mechanical directory actually listed 11 files during this check, with no subdirectories and no STL files. The original STP CAD file for the support cover was obtained, but no corresponding STL was obtained from that directory. This conclusion applies only to the directory checked; it does not establish that the file is unavailable elsewhere online.
- File existence, source, size, Git blob hashes, and format headers were checked. No CAD geometry parsing, dimensional measurement, tolerance checking, print slicing, or manufacturing compatibility verification was performed.
- The `70dts` text in the filename, the part names, and the file formats do not replace dimensional verification. Tooth count, hole geometry, dimensions, units, material, and manufacturing method must be established by checking the file contents, assembly references, and actual vehicle.
- Downloading an STP file does not mean it is ready to print, and downloading a DXF file does not establish the gear manufacturing process. The actual vehicle's gear version, cover mounting points, OPB815WZ optical path, and platform clearance still need checking. No purchasing, machining, drilling, or installation was performed.
