import xarray as xr

file = r"data\raw\rainfall\RF25_ind2024_rfp25.nc"

ds = xr.open_dataset(file)

print("\n========== DATASET ==========")
print(ds)

print("\n========== VARIABLES ==========")
print(ds.data_vars)

print("\n========== COORDINATES ==========")
print(ds.coords)

print("\n========== RAINFALL ==========")
print(ds["RAINFALL"])

ds.close()