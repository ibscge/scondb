import asyncio
import base64
import hashlib
import os
import secrets
import time

import numpy as np
import pandas as pd
import pysam
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse

app = FastAPI()

origins = [
     #"http://118.42.91.16:11156",
]



app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



#df_meta = pd.concat([pd.read_csv('data/scon_output_meta.csv'),
#                    pd.read_csv('scon_outputs/scon_output_meta.csv')]).sort_values(['species', 'ensemble_rev'])
df_meta = pd.read_csv('data/scon_output_meta.csv').sort_values(['species', 'ensemble_rev'])
df_meta['label']=df_meta.apply(lambda x: f"{x.species} {x.grcm_ver} (v.{x.ensemble_rev}) ", axis=1)
df_meta['group_label']=df_meta.apply(lambda x: f"Ensembl ver: {x.ensemble_rev}", axis=1)

def get_group_items(df):
    return df.apply(lambda x: x.to_dict(), axis=1).tolist()

species_group_items = [{'label': name, 'code': name,
                        'ensemble_rev': float(df.iloc[0].ensemble_rev),
                        'items':get_group_items(df)} for name, df in df_meta.groupby('group_label')]

def load_scon_data(scon_file):
    print(f'data/{scon_file.replace(".csv", ".parquet")}')
    df_scon = pd.read_parquet(f'data/{scon_file.replace(".csv", ".parquet")}')
    print(df_scon.shape)
    # df_scon = pd.read_parquet('data/scon_output.MAGR.parquet')
    df_scon.Exon_usage=df_scon.Exon_usage.fillna(0).astype(int)
    df_scon.GC=df_scon.GC.fillna(0).astype(int)
    return df_scon


@app.get('/meta/species_groups')
async def list_species():    
    return species_group_items



@app.get('/meta/species')
async def list_species():
    species = sorted(list(set(df_meta.species)))
    return [{'name':x, 'code':x} for x in species]



@app.get('/meta/dataset')
async def list_dataset(species: str = None):
    if species:
        tmp=df_meta.query(f'species=="{species}"')
    else:
        tmp=df_meta
    if tmp.empty:
        return []
    datasets = [{'key': row.ensemble_rev,
                 'ensemble_rev': row.ensemble_rev,
                 'name': f'{row.grcm_ver} (Ensemble release {row.ensemble_rev})',
                 'dataset': row.scon_file,
                 'species': row.species,
                } for _, row in tmp.iterrows()]
    return datasets


@app.get('/sconable_genes')
async def sconable_genes(species: str, ensemble_rev: int):
    df_row = df_meta.query(f'species=="{species}" and ensemble_rev=={ensemble_rev}')
    if df_row.empty:
        return []
    scon_file = df_row.scon_file.iloc[0]
#     scon_sites = df_scon.query(f'scon_file=="{scon_file}"')
    scon_sites = load_scon_data(scon_file)
    
    return [{'name':x, 'code':x} for x in sorted(set(scon_sites.Gene))]



@app.get('/sconable_sites')
async def sconable_sites(species: str, ensemble_rev: int, gene: str):
    df_row = df_meta.query(f'species=="{species}" and ensemble_rev=={ensemble_rev}')
    if df_row.empty:
        return []
    scon_file = df_row.scon_file.iloc[0]
    df_scon = load_scon_data(scon_file)
    scon_sites = df_scon.query(f'scon_file=="{scon_file}" and Gene=="{gene}"')
    scon_sites.index.name='idx'
    scon_sites= scon_sites.reset_index().replace([np.nan], [None]).to_dict(orient='records')
    return scon_sites


@app.get('/sconable_sites_group')
async def sconable_sites_group(species: str, ensemble_rev: int, gene: str):
    df_row = df_meta.query(f'species=="{species}" and ensemble_rev=={ensemble_rev}')
    if df_row.empty:
        return ['a']
    scon_file = df_row.scon_file.iloc[0]
    df_scon = load_scon_data(scon_file)

    scon_sites = df_scon.query(f'scon_file=="{scon_file}" and Gene=="{gene}"')
    scon_sites= scon_sites.replace([np.nan], [None])
    
    scon_gene = scon_sites#.eval('id=index')    
    scon_gene['id'] = "scon." + scon_sites.Chromosome + "." + scon_sites.Insertion_start.astype(str)
    #return scon_gene.to_dict(orient='records')
    def to_dict(df):        
        row = df.iloc[0].to_dict()
        # cols = 'Gene Chromosome PAM_position Target_length Tartget_start Tartget_end Target_sequence'.split()
        # row['scon_sites']=df[cols+['id']].to_dict(orient='records')
        row['n_editable']=len(df)
        row['scon_sites']=df.to_dict(orient='records')
        return row
    
    cols = 'Gene Chromosome Transcript Exon Exon_usage Exon_size Exon_strand Exon_start Exon_end Insertion_start Insertion_end'.split()
    rows = [to_dict(df) for k, df in scon_gene.groupby(cols)]
#     rows = [k for k, df in scon_gene.groupby(cols)]
    
    return rows


@app.get('/sconable_site_count_by_transcript')
async def sconable_site_count_by_transcript(species: str, ensemble_rev: int, gene: str):
    df_row = df_meta.query(f'species=="{species}" and ensemble_rev=={ensemble_rev}')
    if df_row.empty:
        return []

    scon_file = df_row.scon_file.iloc[0]
    df_scon = load_scon_data(scon_file)

    scon_sites = df_scon.query(f'scon_file=="{scon_file}" and Gene=="{gene}"')
    if scon_sites.empty:
        return []
    scon_site_counts = scon_sites.groupby(['Transcript', 'Exon']).count().Gene.unstack(level=0)
    df_out = scon_site_counts.reset_index().replace(np.nan, None)
    return {'columns':df_out.columns.to_list(), 'rows': df_out.to_dict(orient='records')}


@app.get('/scon_sites_by_transcript')
async def scon_sites_by_transcript(species: str, ensemble_rev: int, exon: str, transcript: str):
    df_row = df_meta.query(f'species=="{species}" and ensemble_rev=={ensemble_rev}')
    if df_row.empty:
        return []

    scon_file = df_row.scon_file.iloc[0]
    scon_output = f'data/{scon_file.replace(".csv", ".parquet")}'
    gtf_file = f'{scon_file.replace(".SCON_DB.csv", "")}'
    gtf_summary = f'ref_data/{gtf_file}.summary.parquet'
    fasta_file = f'ref_data/{gtf_file.replace(f".{ensemble_rev}.gtf", ".dna.toplevel.fa")}'


    df_scon=pd.read_parquet(scon_output)
    df_scon['scon_id'] = "scon." + df_scon.Chromosome + "." + df_scon.Insertion_start.astype(str)

    ref_fasta = pysam.FastaFile(fasta_file)
    scon_seq_info = pd.read_parquet(gtf_summary)

    scon_sites = df_scon.query(f'(Transcript=="{transcript}")&Exon=="{exon}"')
    # gene_info = scon_seq_info.query(f'gene_name=="{gene_name}"')
    gene_info = scon_seq_info.query(f'(feature=="exon")&(exon_id=="{exon}")')

    if scon_sites.empty or gene_info.empty:
        return []


    # gene = gene_info.query('feature=="gene"').iloc[0]
    gene = gene_info.iloc[0]
    print(gene)
    gene_seq = ref_fasta.fetch(gene.chrom, gene.start-1, gene.end)

    len_padding = 0 if (gene.start%100==0) else gene.start%100
    gene_seq = ' '*len_padding + gene_seq #f"{gene.start} {gene.end} {len_padding}"+

    bases = {i:{'chrom': gene.chrom, 'pos':i, 'base':c, 'className':'dna-char'}
            for c, i in zip(gene_seq, range(gene.start-len_padding, gene.end+1))}

    for i in range(gene.start-len_padding, gene.end+1):
        if i%100==99:
            bases[i]['className'] += ' line-break'
        elif i%50==49:
            bases[i]['className'] += ' chunk-sep-sep'
        elif i%10==9:
            bases[i]['className'] += ' chunk-sep'

    for _, exon in gene_info.query('feature=="exon"').iterrows():
        for i in range(exon.start, exon.end+1):
            bases[i]['className'] += ' exon'

    def get_range(start, end):
        if start<end:
            return (start, end+1)
        return (end, start+1)

    for _, scon_site in scon_sites.iterrows():
        scon_idx = scon_site.scon_id
        for i in range(*get_range(scon_site.Insertion_start, scon_site.Insertion_end)):
            bases[i]['className'] += f' scon scon_MAGR {scon_idx}'
            bases[i]['sconIndex']= scon_idx

        for i in range(*get_range(scon_site.Tartget_start, scon_site.Tartget_end)):
            bases[i]['className'] += f' targetX {scon_idx}'
            bases[i]['sconIndex']= scon_idx


        if scon_site.PAM_position == 'left':
            # for i in range(scon_site.Tartget_start, scon_site.Tartget_start+3):
            for i in range(*get_range(scon_site.Tartget_start, scon_site.Tartget_start)):
                bases[i]['className'] += ' left-pam'
        elif scon_site.PAM_position == 'right':
            # for i in range(scon_site.Tartget_end-2, scon_site.Tartget_end+1):
            for i in range(*get_range(scon_site.Tartget_start, scon_site.Tartget_start)):
                bases[i]['className'] += ' right-pam'


    for i, x in bases.items():
        x['className'] = ' '.join(list(set(x['className'].split())))

    seqs = [x for i, x in bases.items()]

    return seqs

