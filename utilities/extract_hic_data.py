import os
import sys
import numpy as np
import hicstraw
import h5py

def extract_hic_data(path, hic_url, resolutions, chromosomes, data_types):
    try:
        hic = hicstraw.HiCFile(hic_url)
    except Exception as e:
        print(f"[ERROR] Failed to create HiCFile object: {e}")
        return

    normalization = 'KR'
    try:
        resolutions = [int(r.strip().strip("'")) for r in resolutions.split(",")]
        chromosomes = [c.strip().strip("'") for c in chromosomes.split(",")]
        data_types = [d.strip().strip("'") for d in data_types.split(",")]
    except Exception as e:
        print(f"[ERROR] Failed to parse inputs: {e}")
        return

    for resolution in resolutions:
        for chromosome in chromosomes:
            startingbp = 0
            try:
                endingbp = hic.getChromosomes()[int(chromosome)].length
            except Exception as e:
                continue

            for data in data_types:
                short_score_file = f'{path}hicFiles/short_score_textform/shortScore_res{resolution}_ch{chromosome}_{data}_{normalization}.txt'
                h5_filename = f'{path}Workspaces/individual/ch{chromosome}_res{resolution}_{data}_{normalization}.h5'

                if os.path.exists(short_score_file) and os.path.exists(h5_filename):
                    print(f"Skipping extraction for Chromosome {chromosome}, Resolution {resolution}, Data {data}: Files already exist.")
                    continue

                try:
                    matrix_object = hic.getMatrixZoomData(chromosome, chromosome, data, normalization, "BP", resolution)
                    matrix = matrix_object.getRecordsAsMatrix(startingbp, endingbp, startingbp, endingbp)
                except Exception as e:
                    print(f"[ERROR] Failed to get matrix data: {e}")
                    continue

                if not os.path.exists(short_score_file):
                    try:
                        with open(short_score_file, 'wt') as fid_org:
                            for i in range(matrix.shape[0]):
                                for j in range(i, matrix.shape[1]):
                                    if matrix[i, j] != 0:
                                        fid_org.write('0 {} {} 0 0 {} {} 1 {:.5f}\n'.format(chromosome, startingbp + resolution * i, chromosome, startingbp + resolution * j, matrix[i, j]))
                    except Exception as e:
                        print(f"[ERROR] Failed to save short form text: {e}")

                if not os.path.exists(h5_filename):
                    try:
                        with h5py.File(h5_filename, 'w') as hf:
                            hf.create_dataset('matrix', data=matrix)
                    except Exception as e:
                        print(f"[ERROR] Failed to save .mat file: {e}")

    for data in data_types:
        combined_file = f'{path}hicFiles/short_score_textform/shortScore_all_{data}_KR.txt'
        if os.path.exists(combined_file):
            print(f"Skipping combined extraction for Data {data}: File already exists.")
            continue

        try:
            with open(combined_file, 'wt') as fid_org:
                for resolution in resolutions:
                    for chromosome in chromosomes:
                        try:
                            startingbp = 0
                            endingbp = hic.getChromosomes()[int(chromosome)].length
                            matrix_object = hic.getMatrixZoomData(chromosome, chromosome, data, "KR", "BP", resolution)
                            matrix = matrix_object.getRecordsAsMatrix(startingbp, endingbp, startingbp, endingbp)
                            for i in range(matrix.shape[0]):
                                for j in range(i, matrix.shape[1]):
                                    if matrix[i, j] != 0:
                                        fid_org.write('0 {} {} 0 0 {} {} 1 {:.5f}\n'.format(chromosome, startingbp + resolution * i, chromosome, startingbp + resolution * j, matrix[i, j]))
                        except Exception as e:
                            print(f"[ERROR] Failed to get matrix data for combined file: {e}")
        except Exception as e:
            print(f"[ERROR] Failed to save combined short form text: {e}")

if __name__ == "__main__":
    data_path = sys.argv[1]
    hic_url = sys.argv[2]
    resolutions_list = sys.argv[3]
    chromosomes_list = sys.argv[4]
    data_types_list = sys.argv[5]
    extract_hic_data(data_path, hic_url, resolutions_list, chromosomes_list, data_types_list)
