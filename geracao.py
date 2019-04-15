#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import random
pathnameto_eppy = '../'
sys.path.append(pathnameto_eppy)

from eppy import modeleditor
from eppy.modeleditor import IDF

from eppy.results import readhtml
from eppy.runner.run_functions import runIDFs

import multiprocessing

import os
import esoreader

idd = "/usr/local/EnergyPlus-8-7-0/Energy+.idd"
fname_VN = "ZB2_VN.idf"
fname_AC = "ZB2_AC.idf"
epw = "RS_pelotas.epw"
version = '8-7-0'

IDF.setiddname(idd)
idf_VN = IDF(fname_VN)
idf_AC = IDF(fname_AC)

materials_VN = idf_VN.idfobjects["MATERIAL"]
materials_AC = idf_VN.idfobjects["MATERIAL"]

cer_eq = materials_VN[4]
arg = materials_VN[5]

EPS = materials_VN[11]
fibrocimento = materials_VN[3]
forro_madeira = materials_VN[2]

radier_conc = materials_VN[0]
arg_piso = materials_VN[1]
rev_cer = materials_VN[7]


building = idf_VN.idfobjects["BUILDING"]

file = open("config.txt","w")
result_AC = open("result_AC.txt", "w")
result_VN = open("result_VN.txt", "w")
 
# FORMULAS PARA RESISTENCIAS ATUAIS DO MODELO;
rt_argamassa = (2*(0.02/1.15))
rt_ar = 0.16
rt_ar_cob = 0.21
rt_telha_fibro = 0.008/0.65
rt_forro_madeira = 0.02/0.12
rt_radier_conc = radier_conc.Thickness/radier_conc.Conductivity
rt_arg_piso = arg_piso.Thickness/arg_piso.Conductivity
rt_rev_cer = rev_cer.Thickness/rev_cer.Conductivity
rt_wall_total = rt_argamassa+((cer_eq.Thickness/cer_eq.Conductivity))+ rt_ar


lista_idfs_VN = []
lista_idfs_AC = []

runs_AC = []
runs_VN = []

lista_tam = 0
paradas = 0
# Geração inicial de 4800 individuos para cada um (VN e AC)
for i in range(4800):

	lista_tam+=1

	# ORIENTACAO
	file.write("C" + str(i) + " ")
	orientation_random = random.randint(1,8)
	idf_VN.idfobjects["BUILDING"][0].North_Axis = orientation_random*45
	idf_AC.idfobjects["BUILDING"][0].North_Axis = orientation_random*45
	file.write("Orientacao: " +str(orientation_random*45)+" ")

	# PAREDES

	wall_random = round(random.uniform(0.3,2.5),2)
	abs_random = round(random.uniform(0.2,0.9),1)
	file.write("U parede: " + str(wall_random)+ " ")
	file.write("Abs. parede: " + str(abs_random)+ " ")
		

	rt_random = 1/wall_random
	new_thickness = (cer_eq.Conductivity*(rt_random - rt_argamassa - rt_ar))/2

	new_CT = 2*(new_thickness*(cer_eq.Specific_Heat/1000)*cer_eq.Density) + 2*(arg.Thickness*(arg.Specific_Heat/1000)*arg.Density) 
	new_density = (new_CT - 2*(arg.Thickness*(arg.Specific_Heat/1000)*arg.Density))/((new_thickness*0.92)*2)
	new_CT = "%.2f" % new_CT

	
	idf_VN.idfobjects["MATERIAL"][4].Thickness = new_thickness
	idf_AC.idfobjects["MATERIAL"][4].Thickness = new_thickness

	idf_VN.idfobjects["MATERIAL"][4].Density = new_density
	idf_AC.idfobjects["MATERIAL"][4].Density = new_density

	idf_VN.idfobjects["MATERIAL"][5].Solar_Absorptance = abs_random
	idf_AC.idfobjects["MATERIAL"][5].Visible_Absorptance = abs_random 

	# COBERTURA

	roof_random = round(random.uniform(0.3,2.3),2)
	abs_random = round(random.uniform(0.2,0.9),1)
	file.write("U cobertura: " + str(roof_random)+ " ")
	file.write("Abs. cobertura: " + str(abs_random)+ " ")

	rt_random_roof = 1/roof_random
	new_thickness_roof = (EPS.Conductivity*(rt_random_roof - rt_ar_cob - rt_forro_madeira - rt_telha_fibro))
	new_CT_roof = (forro_madeira.Thickness*(forro_madeira.Specific_Heat/1000)*forro_madeira.Density)+(new_thickness_roof*(EPS.Specific_Heat/1000)*EPS.Density)+(fibrocimento.Thickness * (fibrocimento.Specific_Heat/1000) * fibrocimento.Density)
	new_density_roof = (new_CT_roof - (forro_madeira.Thickness*(forro_madeira.Specific_Heat/1000)*forro_madeira.Density) - (fibrocimento.Thickness * (fibrocimento.Specific_Heat/1000) * fibrocimento.Density))/(new_thickness_roof*(EPS.Specific_Heat/1000))

	idf_VN.idfobjects["MATERIAL"][11].Thickness = new_thickness_roof
	idf_AC.idfobjects["MATERIAL"][11].Thickness = new_thickness_roof

	idf_VN.idfobjects["MATERIAL"][11].Density = new_density_roof
	idf_AC.idfobjects["MATERIAL"][11].Density = new_density_roof

	idf_VN.idfobjects["MATERIAL"][3].Solar_Absorptance = abs_random 
	idf_VN.idfobjects["MATERIAL"][3].Visible_Absorptance = abs_random	

	# PISO

	floor_random = round(random.uniform(1.0,4.1),2)
	rt_random_floor = 1/floor_random
	new_thickness_floor = (radier_conc.Conductivity*(rt_random_floor - rt_arg_piso - rt_rev_cer))
	new_CT_floor = (new_thickness_floor*(radier_conc.Specific_Heat/1000)*radier_conc.Density)+(arg_piso.Thickness*(arg_piso.Specific_Heat/1000)*arg_piso.Density)+(rev_cer.Thickness*(rev_cer.Specific_Heat/1000)*rev_cer.Density)
	new_density_floor = (new_CT_floor - (arg_piso.Thickness*(arg_piso.Specific_Heat/1000)*arg_piso.Density) - (rev_cer.Thickness*(rev_cer.Specific_Heat/1000)*rev_cer.Density))/(new_thickness_floor*(radier_conc.Specific_Heat/1000))

	idf_VN.idfobjects["MATERIAL"][0].Thickness = new_thickness_floor
	idf_AC.idfobjects["MATERIAL"][0].Thickness = new_thickness_floor

	idf_VN.idfobjects["MATERIAL"][0].Density = new_density_floor
	idf_AC.idfobjects["MATERIAL"][0].Density = new_density_floor

	file.write("U piso: " + str(floor_random)+ " " + "\n")


	nome_VN = "C"+"%d" % i + ' VN' +'.idf'
	nome_AC = "C"+"%d" % i + ' AC' +'.idf'

	idf_VN.saveas('%s' % nome_VN)
	lista_idfs_VN.append(nome_VN)
	idf_AC.saveas('%s' % nome_AC)
	lista_idfs_AC.append(nome_AC)

	if(lista_tam < 100):
		runs_AC.append([modeleditor.IDF(open(nome_AC, 'r'), epw),
	                         {'output_directory': 'C%i AC' % i,'ep_version': version,'expandobjects':True}])
		runs_VN.append([modeleditor.IDF(open(nome_VN, 'r'), epw),
							 {'output_directory': 'C%i VN' % i,'ep_version': version,'expandobjects':True}])

	if(lista_tam == 100):
		paradas += 1
		lista_tam = 0
		print (paradas)
		runIDFs(runs_AC, int(multiprocessing.cpu_count()))
		runIDFs(runs_VN, int(multiprocessing.cpu_count()))
		runs_AC.clear()
		runs_VN.clear()

# RUNIDF sem uso de paralelismo;
'''
for idf in lista_idfs_VN:
	nome = idf.replace('.idf','')
	saida = os.getcwd() + "\%s" % nome
	idf_run = IDF(idf, epw)
	idf_run.run(output_directory=saida,expandobjects=True)

for idf in lista_idfs_AC:
	nome = idf.replace('.idf','')
	saida = os.getcwd() + "\%s" % nome
	idf_run = IDF(idf, epw)
	idf_run.run(output_directory=saida,expandobjects=True)
'''


# RESULTADOS AC
for i in range(len(lista_idfs_AC)):
	fname = "C%d AC/eplustbl.htm"%i
	filehandle = open(fname,'r').read()

	htables = readhtml.titletable(filehandle)
	firstitem = htables[0]
	firstitem_table = firstitem[1]
	secondrow = firstitem_table[2]
	consumo_total = secondrow[1]
	result_AC.write("C%d AC " %i + str(consumo_total) + '\n')

# RESULTADOS VN
for i in range(len(lista_idfs_VN)):
	sum_serie = 0
	path = "C%d VN/eplusout.eso"%i
	dd, data = esoreader.read(path)
	frequency, key, variable = dd.find_variable('Zone Thermal Comfort ASHRAE 55 Adaptive Model 80% Acceptability Status')[0]
	idx = dd.index[frequency, key, variable]
	time_series = data[idx]
	num_hours =8760
	for j in range(8760):
		if time_series[j] > 0 and time_series[j] <= 1:
			sum_serie+=time_series[j]
			#print time_series[j]
		elif time_series[j] == -1:
			num_hours -= 1

	result_VN.write("C%d VN " %i + str((float(sum_serie/num_hours)*100)) + "%" + '\n')		
