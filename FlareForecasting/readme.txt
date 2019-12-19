
Major softwares: Keras2.2.2, Tensorflow1.10.0, Python3.5.5

#########################################################################################

We provide the codes for downloading No-flare/C/M/X-level samples through web spider, the codes for constructing 10 CV data sets by the method of shuffle and split CV based on AR segregation, and the codes for building the proposed CNN model, and training and testing the model on the 10 CV data sets for both >=C-class and >=M-class flare prediction.

1. spider folder: There are two folders in the spider folder: C_M_X spider and No-flare spider, respectively. The codes in the folder of C_M_X spider are used to obtain C/M/X-level samples through web spider. The codes in the folder of No-flare spider are used to obtain the No-flare level samples through web spider. 

2. 2csv.py: This program is used to construct 10 CV data sets by the method of shuffle and split CV based on AR segregation. 

3. Model(N_CMX).py: This program manily includes as following: building the proposed CNN model, and training and testing the model on the 10 CV data sets for the >=C-class flare prediction.

4. Model(NC_MX).py: This program manily includes as following: building the proposed CNN model, and training and testing the model on the 10 CV data sets for the >=M-class flare prediction.


