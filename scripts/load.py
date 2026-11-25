import pandas as pd, glob, re
FILES={'CESA':'Resultados CESA.xlsx','EAFIT':'Resultados EAFIT.xlsx','ICESI':'Resultados ICESI.xlsx','Uninorte':'Resultados uninorte.xlsx'}
def load():
    frames=[]; hdr=None
    for k,f in FILES.items():
        d=pd.read_excel(f,sheet_name='Datos sin procesar',header=None)
        if hdr is None: hdr=[str(x).strip() for x in d.iloc[0]]
        d=d.iloc[1:].copy(); d.columns=range(d.shape[1]); d.insert(0,'archivo',k)
        frames.append(d)
    df=pd.concat(frames,ignore_index=True)
    return df,hdr
