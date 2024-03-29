import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import helper as hlp
import collections
from random import randint

colors = []

for i in range(50):
    colors.append('#'+'%06X' % randint(0, 0xFFFFFF))

# Loading data
#data = np.load('data2D.npy')
data = np.load('data100D.npy')
[num_pts, dim] = np.shape(data)


is_valid = True

# For Validation set
if is_valid:
  valid_batch = int(num_pts / 3.0)
  np.random.seed(45689)
  rnd_idx = np.arange(num_pts)
  np.random.shuffle(rnd_idx)
  val_data = data[rnd_idx[:valid_batch]]
  data = data[rnd_idx[valid_batch:]]
  


# Distance function for K-means
def distanceFunc(X, MU):
    # Inputs
    # X: is an NxD matrix (N observations and D dimensions)
    # MU: is an KxD matrix (K means and D dimensions)
    # Outputs
    # pair_dist: is the pairwise distance matrix (NxK)
    # TODO
    points_expanded = tf.expand_dims(X, 1)
    means_expanded = tf.expand_dims(MU, 0)    
    return tf.reduce_sum(tf.square(points_expanded - means_expanded), 2)


def buildGraph(input_data, cluster_size):
    input_x = tf.placeholder(tf.float32, shape=[None, input_data.shape[1]], name='input_x')
    centroids = tf.Variable(tf.random_normal([cluster_size, input_data.shape[1]], stddev=0.5))
    num_data = tf.placeholder(tf.float32)
    #Calculate the pair-distance matrix
    pair_distance = distanceFunc(input_x, centroids)
    
    #Calculate the loss
    loss = tf.reduce_sum(tf.reduce_min(pair_distance, 1)) / num_data
    #calculate the prediction
    #print(pair_distance.shape)
    prediction = tf.argmin(pair_distance,1)
    #Optimizer
    with tf.name_scope("optimizer"):
        optimizer = tf.train.AdamOptimizer(learning_rate=0.5, beta1=0.9, beta2=0.99, epsilon=1e-5).minimize(loss)
    
    return input_x, centroids, pair_distance, loss, optimizer, prediction, num_data
    
def part_1_plot(k, traindata, cluster, figure_number):

    #cluster_color = ["r","g","b","c","m"] 
    #print (cluster.shape)
    #print(traindata.shape)
    color_of_points = []
    for i in range(len(cluster)):
        color_of_points.append(colors[cluster[i]])
    plt.figure(figure_number)
    plt.title("Classification of points with {} clusters".format(k))
    
    plt.xlim([-4,5])
    plt.ylim([-5,3])
    plt.scatter(traindata[:,0], traindata[:,1], c=color_of_points, marker='.', s=1)

    
def find_distribution (train_prediction, k):
    distribution = []
    distribution.append((collections.Counter(train_prediction)))
    return distribution 
    
    
def main():
    
    cluster_values = [20]
    figure_number = 0
    final_train_loss_values = []
    final_valid_loss_values = []
    final_distribution = []
    
    for k_value in cluster_values:
        #loss values
        train_loss_list = []
        val_train_loss_list = []
        train_loss_value = 0
        val_loss_value = 0
    
        #Build the graph
        input_x, centroids, pair_distance, loss, optimizer, prediction, num_data = buildGraph(data, k_value)
    
        with tf.Session() as sess:
        # Initialize all variables
            sess.run(tf.global_variables_initializer())
            
            # Loop over number of epochs
            for epoch in range(500):
                feed_dict_train = {input_x: data, num_data: data.shape[0]}
                feed_dict_train_val = {input_x: val_data, num_data: val_data.shape[0]}
                #Run the optimizer
                sess.run(optimizer, feed_dict=feed_dict_train)
                
                train_loss_value, train_prediction = sess.run([loss, prediction], feed_dict=feed_dict_train)
                
                val_loss_value, val_train_prediction = sess.run([loss, prediction], feed_dict=feed_dict_train_val)
                #print(train_prediction)
                train_loss_list.append(train_loss_value)
                val_train_loss_list.append(val_loss_value)
                #print("Training data loss: "+str(train_loss_value))
                #print("Valid data loss: " + str(val_loss_value))
         
        
        final_train_loss_values.append(train_loss_value)
        final_valid_loss_values.append(val_loss_value)
        
        plt.figure(k_value)
        plt.plot(train_loss_list, c='b')
        plt.title("Training data loss: Cluster Size of " + str(k_value))
        plt.grid()
        plt.legend(loc='best')
        plt.xlabel('Iteration')
        plt.ylabel('Loss') 
        
        plt.figure(k_value+7)
        plt.plot(val_train_loss_list, c='g')
        plt.title("Validation data loss: Cluster Size of " + str(k_value))
        plt.grid()
        plt.legend(loc='best')
        plt.xlabel('Iteration')
        plt.ylabel('Loss')
        
        
        
        part_1_plot(k_value, data, train_prediction, figure_number)
        figure_number += 1
        part_1_plot(k_value, val_data, val_train_prediction, figure_number) 
        final_distribution.append(find_distribution(train_prediction, k_value))
        final_distribution.append(find_distribution(val_train_prediction, k_value))
        
    for i in final_train_loss_values:
        print("Train loss: "+str(i))
        
    for i in final_valid_loss_values:
        print("Valid loss: "+str(i))
        
    print(final_distribution)
        

if __name__ == "__main__":
    main()
    
    
