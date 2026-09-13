// ============================================================
// DATA LOADER MODULE FOR VIREO
// ============================================================

module data::data_loader

import std::fs
import std::csv
import std::io

// ============================================================
// DATASET STRUCTURE
// ============================================================

pub struct Dataset {
    data: List[Vec<F32>]
    labels: List[Int]
}

pub struct DataLoader {
    dataset: Dataset
    batch_size: Int
    shuffle: Bool
    current_batch: Int
}

// ============================================================
// LOAD DATA FROM CSV
// ============================================================

pub fn load_csv(filename: Str) -> Dataset {
    io::println(f"   📂 Loading data from {filename}...")
    
    let csv_data = csv::read(filename)
    let mut data = []
    let mut labels = []
    
    for row in csv_data {
        let features = row[:-1]
        let label = row[-1] as Int
        
        data.push(features)
        labels.push(label)
    }
    
    io::println(f"   ✅ Loaded {data.len()} samples")
    
    return Dataset {
        data: data,
        labels: labels
    }
}

// ============================================================
// GENERATE SYNTHETIC DATA
// ============================================================

pub fn generate_synthetic_data(n_samples: Int, n_features: Int) -> Dataset {
    io::println(f"   🔧 Generating {n_samples} synthetic samples...")
    
    let mut data = []
    let mut labels = []
    
    for i in 0..n_samples {
        let mut features = []
        for j in 0..n_features {
            features.push(random::float(0.0, 1.0))
        }
        
        let label = features.sum() / n_features > 0.5 ? 1 : 0
        
        data.push(features)
        labels.push(label)
    }
    
    return Dataset {
        data: data,
        labels: labels
    }
}

// ============================================================
// EXPORT
// ============================================================

export Dataset, DataLoader
export load_csv, generate_synthetic_data