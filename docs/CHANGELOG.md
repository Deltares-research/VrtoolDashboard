# Changelog

## v0.0.0 [##/##/####]

### Added
- Added flood_damages attribute to DikeSection
- Added total damages and risk to Area stats

### Changed
None.

### Deprecated
None.

### Removed
None.

### Fixed
None.

## v0.6.1 [25/09/2024]

### Added
- Added radio result type in projects page
- Added all trajects on map in projects page
- Added name input field to save projects
- Added basic areal stats to projects page

### Changed
- Vrtool core 1.0.1
- Upgrade to MapLibre
- Colorscale for verhouding vr/dsn

### Deprecated
None.

### Removed
None.

### Fixed
None.

## v0.6.0 [19/09/2024]

### Added
- Safe remove of all custom measures in the database.
- Project Page
- Creation of new projects from user inputs
- Display anchored piles

### Changed
_ Maatregelen tab only shows measures before the final optimization step (eco optimum)
- Disable POST and GET message in terminal in production
- Adding custom measures now creates a backup of the db and modified in place the current one.
- Switching pages keeps the options of dropdown menu "Optimization run selection"
- Custom measure tables: Section is now dropdown
- Custom measure tables: Display all measures of the database in the table
- Custom measure tables: Modal to indicate when a measure is added to the database.

### Deprecated
None.

### Removed
None.

### Fixed
-  Bug traject faalkans with bekleding
-  Bug traject faalkans with years 
- Visualisation maatregel vertical oplossing piping
- Bug in optimization table with toggle Versterking

## v0.5.0 [08/07/2024]

### Added
- Graph comparison measures
- Click event to display measure reliability over time
- click event to highlight combined measures
- Switch back to economic optimal possible
- Custom measures can be imported & displayed in Dashboard.
- Custom measures table and connection with the database.

### Changed
- vrtool 0.3.1
- use times in config.T across the whole dashboard instead of first section times. 

### Deprecated
None.

### Removed
- tests with deprecated databases

### Fixed
- legend duidingsklassen
- Various UI string fixes
- fix run optimize for revetment case
- fix various bugs with mechanism strings
- fix visualisation bug for maatregel Grondversterkingmetstabiliteitscherm.

## v0.4.1 [21/05/2024]

### Added
None.

### Changed
None.

### Deprecated
None.

### Removed
None.

### Fixed
- HotFix for Revetment probability of traject failure

## v0.4.0 [29/04/2024]

### Added
- Acceptance test for DikeTraject importer
- Acceptance test for DikeTraject faalkans matrix
- New attribute greedy steps to DikeTraject
- New attribute active_mechanisms to DikeSection
- Display greedy steps on graph beta vs cost along vr and dsn
- Button recompute to generate a new vr line with specification year/beta
- new buttons to download geojson content of the diketraject.
- Database without doorsnede results can be imported
- Database without any optimization results can be imported
- Added link to the documentation
- Added WBI classes to result maps

### Changed
- Optimize callacbk switched to background callback
- Refactor import od DikeTraject from database
- LCC from database is now already accumulated

### Deprecated
None.

### Removed
-  Custom VRtool logger
- Remove combination of betas for piping VZG+Soil

### Fixed
- Fixed measure name for 3 combined measures
- Fixed investement year for 2/3 combined measures

## v0.3.2 [09/02/2024]

### Added
None.

### Changed
- no display of Soil reinforcement when dberm=dcrest=0

### Deprecated
None.

### Removed
None.

### Fixed
- wrong measure params fetched from database

## v0.3.1 [11/12/2023]

### Added
None.

### Changed
None.

### Deprecated
None.

### Removed
None.

### Fixed
Bug Diaphram Wall + aanpassing bekledin

## v0.3.0 [11/12/2023]

### Added
Integration database to dashboard (Initial assessment + Optimization results)
Modal and display of VRTOOL logging when running optimization
Support of revement cases with database

### Changed
How data is initialized in the dashboard
Wheels of VRCrool v0.1.1
Changed optimization DataTable to Ag Grid
Maatregel type map 

### Deprecated
None.

### Removed
CSv related methods and importers
Temporary signalering and ondergrens NumberFields

### Fixed
Fixed LCC cost

## v0.2.3 [19/10/2023]

### Added
Revetment

### Changed
None.

### Deprecated
None.

### Removed
None.

### Fixed
None.

## v0.2.2 [04/10/2023]

### Added
- Added temporary fields for signaleringswaarde and ondergrens

### Changed
None.

### Deprecated
None.

### Removed
None.

### Fixed
- Fix import of 16_1 / 53_1 and 38_1

## v0.2.1 [04/08/2023]

### Added
None.

### Changed
None.

### Deprecated
None.

### Removed
None.

### Fixed
small bug fixes

## v0.2.0 [04/08/2023]

### Added
Map of measure types, berm widening and crest heightening.

### Changed
None.

### Deprecated
None.

### Removed
None.

### Fixed
None.

## v0.1.0 [17/07/2023]

### Added
First version of the dashboard presented for the demo at the Gebruikersdag 14/07/2023.

### Changed
None.

### Deprecated
None.

### Removed
None.

### Fixed
Fixed bug verhouding vr / dsn returning an error.

## v0.0.0 [21/06/2023]
### Added
Environment related files
- `pyproject.toml`: Poetry configuration file.
- `poetry.lock`: Poetry lock file.

### Changed
None.

### Deprecated
None.

### Removed
None.

### Fixed
None.

