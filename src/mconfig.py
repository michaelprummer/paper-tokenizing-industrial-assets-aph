#######################################
# Hash and Image configuration
#######################################

config = {
    "ave_threshold": 0.9,  # Greater x against the ave_hash to be
    "ave_threshold_versions": 0.8,
    "resolution_scale_width": [0.5, 2],
    "crop_sizes": [0.97, 0.98, 0.99],
    "mpl_tile_sizes": [0.1, 1],
    "mpl_tile_angle": [90, 180],
    "reports_output": "./reports",
    "hash_sizes": [4, 8, 16, 32],
    "high_freq_factor": 6,
    "phash_resize_mode": "nofit",
    "hash_sizes-dev": [8]
}

All = 9001
Some = 12
