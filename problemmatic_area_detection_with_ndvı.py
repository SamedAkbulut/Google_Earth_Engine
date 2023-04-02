# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 13:44:54 2023

@author: bjk_a
"""

import os
import numpy as np
import imageio
import imageio.v2 as imageio
from PIL import Image


def find_tiff(path):
    tif_files = []
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in [f for f in filenames if f.endswith(".tif")]:
            tif_files.append(os.path.join(dirpath, filename))
    tif_files.sort()
    return tif_files


def tiff_to_array(tiff_files):
    arrays = []
    for tiff_file in tiff_files:
        array = np.array(imageio.imread(tiff_file), dtype=np.float32)
        arrays.append(array)
    return arrays


def find_lowest_10_percentile(arrays):
    lowest_10_percentiles = []
    for array in arrays:
        # Get the sorted array without NaNs
        sorted_array = np.sort(array[~np.isnan(array)])

        # Calculate the percentile of the 15th lowest value that is not -0.02, -0.01, 0, 0.01, or 0.02
        lowest_values = sorted_array[(sorted_array > -0.02) & (sorted_array < 0.02) & (sorted_array != 0)]
        lowest_non_outliers = sorted_array[~np.isin(sorted_array, lowest_values)]
        lowest_10_percentiles = [np.percentile(lowest_non_outliers, 15)]
    return lowest_10_percentiles


def mark_lowest_10_percentile(arrays, lowest_10_percentiles):
    masks = []
    for array, lowest_10_percentile in zip(arrays, lowest_10_percentiles):
        mask = np.zeros_like(array, dtype=np.uint8)
        mean_value = np.mean(array[~np.isnan(array)])
        if np.abs(mean_value - np.mean(lowest_10_percentile)) >= 0.02:
            mask[array <= np.percentile(lowest_10_percentile, 85)] = 1
        masks.append(mask)
    return masks


def sum_masks(masks):
    combined_mask = np.zeros_like(masks[0], dtype=np.uint8)
    for mask in masks:
        combined_mask += mask
    combined_mask[combined_mask == 2] = 2  # 2+2=2
    return combined_mask


def export_arrays_as_tiff(arrays, tiff_files, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for i, (array, tiff_file) in enumerate(zip(arrays, tiff_files)):
        tiff_filename = os.path.basename(tiff_file)
        output_path = os.path.join(output_folder, tiff_filename)
        result = Image.fromarray(array)
        result.save(output_path)

        if i < len(arrays) - 1:
            next_tiff_filename = os.path.basename(tiff_files[i+1])
            output_path = os.path.join(output_folder, f"{tiff_filename}+{next_tiff_filename}")
            mask_sum = sum_masks([arrays[i], arrays[i+1]])
            result = Image.fromarray(mask_sum)
            result.save(output_path)


if __name__ == '__main__':
    tiff_path = "C:/Users/bjk_a/590931buffer"
    tiff_files = find_tiff(tiff_path)
    arrays = tiff_to_array(tiff_files)
    lowest_10_percentiles = find_lowest_10_percentile(arrays)
    masks = mark_lowest_10_percentile(arrays, lowest_10_percentiles)
    export_arrays_as_tiff(masks, tiff_files, "590931buffer_05_02")
    
