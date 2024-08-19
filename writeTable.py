from analysis import *
import csv


import tkinter as tk
from tkinter import filedialog


cwd = os.getcwd()
root = tk.Tk()
root.withdraw()

sourceDir = filedialog.askdirectory(initialdir=os.getcwd(), title='Select Folder')
dirName = sourceDir
baseName = os.path.basename(dirName)[:-7]
csvPath = os.path.join(dirName, baseName + '.csv')

if not os.path.exists(csvPath):
    with open(csvPath, 'w') as csvfile:
        writer = csv.writer(csvfile)
        header1 = ['Sample','','','','','',
                      'Total Growth Plate','','','','','','','','',
                      'Germinal Zone','','','','','','','','','','',
                      'Columnar Zone','','','','','','','','','','',
                      'Prehypertrophyic Zone','','','','','','','','','','',
                      'Hypertrophic Zone','','','','','','','','','','',
                      'Total Metaphysis Zone','','','','','','','','',
                      'Preosogenic Metaphyseal Zone','','','','','','','','','','',
                      'Osteogenic Metaphyseal Zone','','','','','','','','','','',
                      ]
        writer.writerow(header1)
        header2 = ['','','','','','',
                  'Borders','','','','Vertical Distance','','Width', 'Area','',
                  'Borders','','','','Vertical Distance','','Width', 'Area','','% Total', '',
                  'Borders','','','','Vertical Distance','','Width', 'Area','','% Total', '',
                  'Borders','','','','Vertical Distance','','Width', 'Area','','% Total', '',
                  'Borders','','','','Vertical Distance','','Width', 'Area','','% Total', '',
                  'Borders','','','','Vertical Distance','','Width', 'Area','',
                  'Borders','','','','Vertical Distance','','Width', 'Area','','% Total', '',
                  'Borders','','','','Vertical Distance','','Width', 'Area','','% Total', '',
                  ]
        writer.writerow(header2)
        header3 = ['Sample #', 'Sample ID', 'Genotype', 'Sex', 'Age', 'Level',
                   'Upper Line', 'Lower Line', 'Left Side', 'Right Side', 'Mean', 'SD','','Mean','SD',
                   'Upper Line', 'Lower Line', 'Left Side', 'Right Side', 'Mean', 'SD','','Mean','SD','Mean','SD',
                   'Upper Line', 'Lower Line', 'Left Side', 'Right Side', 'Mean', 'SD','','Mean','SD','Mean','SD',
                   'Upper Line', 'Lower Line', 'Left Side', 'Right Side', 'Mean', 'SD','','Mean','SD','Mean','SD',
                   'Upper Line', 'Lower Line', 'Left Side', 'Right Side', 'Mean', 'SD','','Mean','SD','Mean','SD',
                   'Upper Line', 'Lower Line', 'Left Side', 'Right Side', 'Mean', 'SD','','Mean','SD',
                   'Upper Line', 'Lower Line', 'Left Side', 'Right Side', 'Mean', 'SD','','Mean','SD','Mean','SD',
                   'Upper Line', 'Lower Line', 'Left Side', 'Right Side', 'Mean', 'SD','','Mean','SD','Mean','SD',
                   ]
        writer.writerow(header3)

with open(csvPath, 'a') as csvfile:
    writer = csv.writer(csvfile)
    recordsDir = os.path.join(dirName,'Records')
    if not os.path.exists(recordsDir):
        os.mkdir(recordsDir)

    TotalGPMean, TotalGPSD, TotalGPStart, TotalGPEnd = getArea(os.path.join(dirName, os.path.join('LineData', 'SOGUL.npy')),
                                                            os.path.join(dirName, os.path.join('LineData', 'DPUCL.npy')),
                                                            os.path.join(recordsDir, 'TotalGP.png'))

    GerminalMean, GerminalSD, GerminalStart, GerminalEnd = getArea(os.path.join(dirName, os.path.join('LineData', 'SOGUL.npy')),
                                                            os.path.join(dirName, os.path.join('LineData', 'C5GLL.npy')),
                                                            os.path.join(recordsDir, 'Germinal.png'))
    

    ColumnarMean, ColumnarSD, ColumnarStart, ColumnarEnd = getArea(os.path.join(dirName, os.path.join('LineData', 'C5GLL.npy')),
                                                            os.path.join(dirName, os.path.join('LineData', 'DPUSL.npy')),
                                                            os.path.join(recordsDir, 'Columnar.png'))
    
    PreHTMean, PreHTSD, PreHTStart, PreHTEnd = getArea(os.path.join(dirName, os.path.join('LineData', 'D0CAP.npy')),
                                                            os.path.join(dirName, os.path.join('LineData', 'D0CML.npy')),
                                                            os.path.join(recordsDir, 'PreHypertrophic.png'))
    
    HTMean, HTSD, HTStart, HTEnd = getArea(os.path.join(dirName, os.path.join('LineData', 'D0CML.npy')),
                                                            os.path.join(dirName, os.path.join('LineData', 'DPUCL.npy')),
                                                            os.path.join(recordsDir, 'Hypertrophic.png'))
    
    MetaphysisMean, MetaphysisSD, MetaphysisStart, MetaphysisEnd = getArea(os.path.join(dirName, os.path.join('LineData', 'DPUCL.npy')),
                                                            os.path.join(dirName, os.path.join('LineData', 'DPUML.npy')),
                                                            os.path.join(recordsDir, 'TotalMetaphysis.png'))
    
    PreMetMean, PreMetSD, PreMetStart, PreMetEnd = getArea(os.path.join(dirName, os.path.join('LineData', 'DPUCL.npy')),
                                                            os.path.join(dirName, os.path.join('LineData', 'C5MUL.npy')),
                                                            os.path.join(recordsDir, 'PreosteogenicMetaphyseal.png'))
    
    OstMetMean, OstMetSD, OstMetStart, OstMetEnd = getArea(os.path.join(dirName, os.path.join('LineData', 'C5MUL.npy')),
                                                            os.path.join(dirName, os.path.join('LineData', 'DPUML.npy')),
                                                            os.path.join(recordsDir, 'OsteogenicMetaphyseal.png'))
    
    sInd = baseName.find('_s')

    rowData = [
        baseName[sInd + 2], # Sample #
        baseName[:sInd], # Sample ID
        baseName[:3], # Genotype
        baseName[sInd - 3], # Sex
        '', # Age
        baseName[sInd - 1], # Level
        'SOGUL', # Upper Line - Total Growth Plate
        'DPUCL', # Lower Line
        TotalGPStart, # Left Side
        TotalGPEnd, # Right Side
        TotalGPMean, # Vertical Distance Mean
        TotalGPSD, # Vertical Distance SD
        TotalGPEnd - TotalGPStart, # Width
        (TotalGPEnd - TotalGPStart) * TotalGPMean, # Area Mean
        (TotalGPEnd - TotalGPStart) * TotalGPSD, # Area SD
        'SOGUL', # Upper Line - Germinal Zone
        'C5GLL', # Lower Line
        GerminalStart, # Left Side
        GerminalEnd, # Right Side
        GerminalMean, # Vertical Distance Mean
        GerminalSD, # Vertical Distance SD
        GerminalEnd - GerminalStart, # Width
        (GerminalEnd - GerminalStart) * GerminalMean, # Area Mean
        (GerminalEnd - GerminalStart) * GerminalSD, # Area SD
        GerminalMean/TotalGPMean, # % Total Mean
        GerminalSD/TotalGPSD, # % Total SD
        'C5GLL', # Upper Line - Columnar Zone
        'DPUSL', # Lower Line
        ColumnarStart, # Left Side
        ColumnarEnd, # Right Side
        ColumnarMean, # Vertical Distance Mean
        ColumnarSD, # Vertical Distance SD
        ColumnarEnd - ColumnarStart, # Width
        (ColumnarEnd - ColumnarStart) * ColumnarMean, # Area Mean
        (ColumnarEnd - ColumnarStart) * ColumnarSD, # Area SD
        ColumnarMean/TotalGPMean, # % Total Mean
        ColumnarSD/TotalGPSD, # % Total SD
        'D0CAP', # Upper Line - Prehypertrophyic Zone
        'D0CML', # Lower Line
        PreHTStart, # Left Side
        PreHTEnd, # Right Side
        PreHTMean, # Vertical Distance Mean
        PreHTSD, # Vertical Distance SD
        PreHTEnd - PreHTStart, # Width
        (PreHTEnd - PreHTStart) * PreHTMean, # Area Mean
        (PreHTEnd - PreHTStart) * PreHTSD, # Area SD
        PreHTMean/TotalGPMean, # % Total Mean
        PreHTSD/TotalGPSD, # % Total SD
        'D0CML', # Upper Line - Hypertrophic Zone
        'DPUCL', # Lower Line
        HTStart, # Left Side
        HTEnd, # Right Side
        HTMean, # Vertical Distance Mean
        HTSD, # Vertical Distance SD
        HTEnd - HTStart, # Width
        (HTEnd - HTStart) * HTMean, # Area Mean
        (HTEnd - HTStart) * HTSD, # Area SD
        HTMean/TotalGPMean, # % Total Mean
        HTSD/TotalGPSD, # % Total SD
        'DPUCL', # Upper Line - Total Metaphysis Zone
        'DPUML', # Lower Line
        MetaphysisStart, # Left Side
        MetaphysisEnd, # Right Side
        MetaphysisMean, # Vertical Distance Mean
        MetaphysisSD, # Vertical Distance SD
        MetaphysisEnd - MetaphysisStart, # Width
        (MetaphysisEnd - MetaphysisStart) * MetaphysisMean, # Area Mean
        (MetaphysisEnd - MetaphysisStart) * MetaphysisSD, # Area SD
        'DPUCL', # Upper Line - Preosogenic Metaphyseal Zone
        'C5MUL', # Lower Line
        PreMetStart, # Left Side
        PreMetEnd, # Right Side
        PreMetMean, # Vertical Distance Mean
        PreMetSD, # Vertical Distance SD
        PreMetEnd - PreMetStart, # Width
        (PreMetEnd - PreMetStart) * PreMetMean, # Area Mean
        (PreMetEnd - PreMetStart) * PreMetSD, # Area SD
        PreMetMean/MetaphysisMean, # % Total Mean
        PreMetSD/MetaphysisSD, # % Total SD
        'C5MUL', # Upper Line - Osteogenic Metaphyseal Zone
        'DPUML', # Lower Line
        OstMetStart, # Left Side
        OstMetEnd, # Right Side
        OstMetMean, # Vertical Distance Mean
        OstMetSD, # Vertical Distance SD
        OstMetEnd - OstMetStart, # Width
        (OstMetEnd - OstMetStart) * OstMetMean, # Area Mean
        (OstMetEnd - OstMetStart) * OstMetSD, # Area SD
        OstMetMean/MetaphysisMean, # % Total Mean
        OstMetSD/MetaphysisSD, # % Total SD
    ]
    writer.writerow(rowData)