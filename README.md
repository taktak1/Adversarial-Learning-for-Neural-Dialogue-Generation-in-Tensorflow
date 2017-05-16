# Adversarial-Learning-for-Neural-Dialogue-Generation-in-Tensorflow

 Adversarial Learning for Neural Dialogue Generation tensorflow1.0 python3.5 version ：https://arxiv.org/pdf/1701.06547.pdf

内容： 

TensorFlow 1.0  Python 3.5

What is al_neural_dialogue：

1.filename

  data：         data；
  
 train_data：    traindata；
 
  disc：         discriminator；
  
  gen:           generator；
  
 utils：         utilities:

2.runfile

al_neural_dialogue_train.py  :   training run file

3.discription


about "al_neural_dialogue_train.py" main function

def main(_):
    #disc_pre_train()   discriminator pre training；
    #gen_pre_train()   generator pre training；
    al_train()        Seq2seqGanTraining；	
	
	
Adversarial-Learning-for-Neural-Dialogue-Generation-in-Tensorflow for TF1.0 & Python3：

1、Discriminator LSTM（[based on liuyuemaicha](http://histudy.doorkeeper.jp/)）

2、generator Seq2Seq（TensorFlow original）

3、seq2seq GAN Monte Carlo Search（beam search）

