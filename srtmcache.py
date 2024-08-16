# TerraShade
# Copyright (C) 2024  Andreas Stamos
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import earthaccess
import rasterio
import tempfile
import os
import shutil
import zipfile

class SRTMCache:
    def __init__(self, buffer=0.01):
        auth = earthaccess.login()
        self.temp_dir = tempfile.mkdtemp()
        self.tiles = {}

    def _download_tile(self, lat, lon):
        results = earthaccess.search_data(
            short_name="SRTMGL1",
            bounding_box=(lon, lat, lon, lat)
        )

        if not results:
            raise ValueError("No SRTM data found for the given location.")

        f = earthaccess.download(results[0], local_path=self.temp_dir)

        with zipfile.ZipFile(f[0], 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)

        hgt_file_path = [os.path.join(self.temp_dir, fn) for fn in os.listdir(self.temp_dir) if fn.endswith('.hgt')][0]

        f = rasterio.open(hgt_file_path)
        dem = f.read(1)
        self.tiles[(int(lat), int(lon))] = (f,dem)

    def get_elevation(self, lat, lon):
        key = (int(lat), int(lon))
        if key not in self.tiles:
            self._download_tile(lat, lon)
        
        tile = self.tiles[key]
        row, col = tile[0].index(lon, lat)
        return tile[1][row,col]

    def close(self):
        for _, (f, _) in self.tiles.items():
            f.close()
        self.tiles.clear()
        shutil.rmtree(self.temp_dir)

