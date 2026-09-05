import os
import re
import pdfplumber
import pandas as pd


PDF_FILE = r"data\raw\landslide\landslide_report.pdf"

OUTPUT_FILE = (
    r"data\processed\landslide\landslide_inventory.csv"
)


if not os.path.exists(PDF_FILE):
    raise FileNotFoundError(
        f"PDF not found:\n{PDF_FILE}"
    )


print("=" * 60)
print("LANDSLIDE INVENTORY EXTRACTION")
print("=" * 60)


records = []


with pdfplumber.open(PDF_FILE) as pdf:

    total_pages = len(pdf.pages)

    print(f"PDF pages: {total_pages:,}")

    for page_no, page in enumerate(pdf.pages, start=1):

        tables = page.extract_tables()

        for table in tables:

            if not table:
                continue

            for row in table:

                if not row:
                    continue

                cells = []

                for cell in row:
                    if cell is None:
                        cells.append("")
                    else:
                        cell = str(cell)
                        cell = cell.replace("\n", " ")
                        cell = " ".join(cell.split())
                        cells.append(cell)

                # Need at least the main fields
                if len(cells) < 8:
                    continue

                # Ignore headers
                joined = " ".join(cells).lower()

                if (
                    "slide_no" in joined
                    or "latitude" in joined
                    or "longitude" in joined
                ):
                    continue

                # First field must look like serial number
                if not re.fullmatch(
                    r"\d+",
                    cells[0].strip()
                ):
                    continue

                # Find latitude and longitude
                lat_index = None

                for i, cell in enumerate(cells):

                    if re.fullmatch(
                        r"-?\d+(?:\.\d+)?",
                        cell.strip()
                    ):

                        value = float(cell)

                        if 6 <= value <= 38.5:
                            lat_index = i
                            break

                if lat_index is None:
                    continue

                # Longitude should immediately follow latitude
                if lat_index + 1 >= len(cells):
                    continue

                try:
                    latitude = float(
                        cells[lat_index]
                    )

                    longitude = float(
                        cells[lat_index + 1]
                    )

                except ValueError:
                    continue

                if not (
                    66 <= longitude <= 100.5
                ):
                    continue

                records.append({
                    "Sl.No.": cells[0],
                    "Slide_No": (
                        cells[1]
                        if len(cells) > 1
                        else ""
                    ),
                    "State": (
                        cells[2]
                        if len(cells) > 2
                        else ""
                    ),
                    "District": (
                        cells[3]
                        if len(cells) > 3
                        else ""
                    ),
                    "Slide_Name": (
                        cells[4]
                        if len(cells) > 4
                        else ""
                    ),
                    "NH_SH_Location": (
                        cells[5]
                        if len(cells) > 5
                        else ""
                    ),
                    "Latitude": latitude,
                    "Longitude": longitude,
                    "Material_Involved": (
                        cells[lat_index + 2]
                        if len(cells) > lat_index + 2
                        else ""
                    ),
                    "Movement_Type": (
                        cells[lat_index + 3]
                        if len(cells) > lat_index + 3
                        else ""
                    ),
                    "History": (
                        cells[lat_index + 4]
                        if len(cells) > lat_index + 4
                        else ""
                    ),
                    "source_page": page_no
                })

        if page_no % 50 == 0:
            print(
                f"Processed {page_no:,} / "
                f"{total_pages:,} pages | "
                f"records found: {len(records):,}"
            )


# ============================================================
# CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(records)


if df.empty:

    raise RuntimeError(
        "No records were extracted. "
        "The PDF table layout needs another extraction method."
    )


# ============================================================
# CLEAN DATA
# ============================================================

df["Sl.No."] = pd.to_numeric(
    df["Sl.No."],
    errors="coerce"
)

df["Latitude"] = pd.to_numeric(
    df["Latitude"],
    errors="coerce"
)

df["Longitude"] = pd.to_numeric(
    df["Longitude"],
    errors="coerce"
)


# Remove invalid coordinates
df = df[
    df["Latitude"].between(6, 38.5)
    &
    df["Longitude"].between(66, 100.5)
].copy()


# Remove duplicate records
before = len(df)

df = df.drop_duplicates(
    subset=[
        "Sl.No.",
        "Latitude",
        "Longitude"
    ]
).reset_index(drop=True)

duplicates = before - len(df)


# ============================================================
# SAVE
# ============================================================

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 60)
print("EXTRACTION COMPLETE")
print("=" * 60)

print(
    f"Records extracted:     {len(df):,}"
)

print(
    f"Duplicates removed:    {duplicates:,}"
)

print(
    f"Valid coordinates:     "
    f"{df[['Latitude','Longitude']].notna().all(axis=1).sum():,}"
)

print(
    f"States found:          "
    f"{df['State'].nunique():,}"
)

print()
print("State distribution:")

print(
    df["State"]
    .value_counts()
    .head(25)
    .to_string()
)

print()
print("First 10 records:")

print(
    df.head(10).to_string(index=False)
)

print()
print("Saved to:")

print(OUTPUT_FILE)