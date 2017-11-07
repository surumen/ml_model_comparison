
from numpy.random import uniform
from numpy.random import randn
import random
import time

import matplotlib.pyplot as plt

from scipy.linalg import eig
from scipy.linalg import sqrtm
from numpy.linalg import inv
from numpy.linalg import svd

from utils import create_one_hot_label
from utils import subtract_mean_from_data
from utils import compute_covariance_matrix

import numpy as np
import numpy.linalg as LA

import sys
from numpy.linalg import svd



class Project2D(): 

	'''
	Class to draw projection on 2D scatter space
	'''

	def __init__(self,projection, clss_labels):

		self.proj = projection
		self.clss_labels = clss_labels


	def project_data(self,X,Y,white=None): 

		'''
		Takes list of state space and class labels
		State space should be 2D
		Labels shoud be int
		'''

		p_a = []
		p_b = []
		p_c = []

		# Project all Data
		proj = np.matmul(self.proj,white)
	
		X_P = np.matmul(proj,np.array(X).T)
		
		for i in range(len(Y)):

			if Y[i] == 0: 
				p_a.append(X_P[:,i])
			elif Y[i] == 1: 
				p_b.append(X_P[:,i])
			else:
				p_c.append(X_P[:,i])

		
		p_a = np.array(p_a)
		p_b = np.array(p_b)
		p_c = np.array(p_c)

		plt.scatter(p_a[:,0],p_a[:,1],label = 'apple')
		plt.scatter(p_b[:,0],p_b[:,1],label = 'banana')
		plt.scatter(p_c[:,0],p_c[:,1],label = 'eggplant')

		plt.legend()

		plt.show()



class Projections():

	def __init__(self,dim_x,classes):

		'''
		dim_x: the dimension of the state space x 
		classes: The list of class labels 
		'''

		self.d_x = dim_x
		self.NUM_CLASSES = len(classes)
		


	def get_random_proj(self):
		'''
		Return A which is size 2 by 729
		'''
		a_random = np.random.standard_normal(2*729)
		a_random = a_random.reshape(2, 729)
		A = np.asmatrix(a_random)
		return A



	def pca_projection(self,X,Y):

		'''
		Return U_2^T
		'''
		Y_one_hot = create_one_hot_label(Y, 729)
		#perform mean subtraction
		X_new, Y_new = subtract_mean_from_data(X, Y_one_hot)
		#compute covariance matrix
		cov_matrix = compute_covariance_matrix(X_new, Y_new)
		#svd decomposition
		U, sigma, V_transpose = LA.svd(cov_matrix, full_matrices=False)

		return np.dot(U, np.dot(np.diag(sigma), V_transpose.T))



	def cca_projection(self,X,Y,k=2):

		'''
		Return U_K^T, \Simgma_{XX}^{-1/2}
		'''
		
		###SCALE AN IDENTITY MATRIX BY THIS TERM AND ADD TO COMPUTED COVARIANCE MATRIX TO PREVENT IT BEING SINGULAR ###
		reg = 1e-5
		#number of classes for this part is 3
		y_one_hot = create_one_hot_label(Y, 3)
		#perform mean subtraction
		X_new, Y_new = subtract_mean_from_data(X, y_one_hot)

		m = X_new.shape[1]
		n = Y_new.shape[1]
		XX = np.dot(X_new.T, X_new)
		YY = np.dot(Y_new.T, Y_new)
		#compute the trace of each matrix
		XX += np.trace(XX)**reg**np.eye(m)
		YY += np.trace(YY)**reg**np.eye(n)
		#compute the inverses
		XX_inverse = inv(sqrtm(XX)).T
		YY_inverse = inv(sqrtm(YY)).T
		#correlation X and Y
		correlation_XY = np.dot(np.dot(X_new, XX_inverse).T, np.dot(Y_new, YY_inverse))
		#finally svd decomposition
		U, sigma, V = svd(correlation_XY)

		#first two columns only
		U = U[:, :2]
		return U.T, sigma




	def project(self,proj,white,X):
		'''
		proj, numpy matrix to perform projection
		whit, numpy matrix to perform whitenting
		X, list of states
		'''

		proj = np.matmul(proj,white)
	
		X_P = np.matmul(proj,np.array(X).T)

		return list(X_P.T)



if __name__ == "__main__":

	X = list(np.load('little_x_train.npy'))
	Y = list(np.load('little_y_train.npy'))

	CLASS_LABELS = ['apple','banana','eggplant']

	feat_dim = max(X[0].shape)
	projections = Projections(feat_dim,CLASS_LABELS)


	# rand_proj = projections.get_random_proj()
	# # Show Random 2D Projection
	# proj2D_viz = Project2D(rand_proj,CLASS_LABELS)
	# proj2D_viz.project_data(X,Y, white = np.eye(feat_dim))

	#PCA Projection 
	# pca_proj = projections.pca_projection(X,Y)
	
	# #Show PCA 2D Projection
	# proj2D_viz = Project2D(pca_proj,CLASS_LABELS)
	# proj2D_viz.project_data(X,Y, white = np.eye(feat_dim))

	#CCA Projection 
	cca_proj,white_cov = projections.cca_projection(X,Y)
	#Show CCA 2D Projection
	proj2D_viz = Project2D(cca_proj,CLASS_LABELS)
	proj2D_viz.project_data(X,Y,white = white_cov)
