# high_env_simulator
This repository is based on the [Highway-env](https://github.com/eleurent/highway-env) and aims to compare different lane change method's performances.

## Env config.
The env distribution of the simulator will affect the mothod performance. And a perfect simulator shoule have a realistic env and can focus on difficult parts. 
Currently, speed distribution of ego car and obstacles, obstacles num, average distance between obstacles, lane num, lane change direction and so on.

### Speed distribution
The speed of ego car and lane change window have a huge impact on lane change motion. A typically overall speed distribution is seems like the following.

![speed distribution fig](https://user-images.githubusercontent.com/80379828/112961465-fa375c80-9177-11eb-850e-36b0ed17822b.png "speed_distribution_fig")

Firstly, we sample ego speed 
![](http://latex.codecogs.com/svg.latex?V_{ego})
and obs speed 
![](http://latex.codecogs.com/svg.latex?V_{obs})
For each obs speed, we sampele the velocity 
![](http://latex.codecogs.com/svg.latex?V_{0bs_i})
from a narrow norm distribution with loc=
![](http://latex.codecogs.com/svg.latex?V_{obs_i})
scale = 
![](http://latex.codecogs.com/svg.latex?V_{obs_i}^{0.5})

![A toy obstacles example with 30 overall obs speed](https://user-images.githubusercontent.com/80379828/112961543-0de2c300-9178-11eb-98b6-3c76b9bbd61d.png "an obs speed distribution")

### Obs num
The more obstacles, the more difficult to lane change. To ensure a relistic and difficult lane change scenario, we set 
![](https://latex.codecogs.com/svg.image?N_{obs}=Int(N(8,&space;2))&space;)
![obs num distribution](https://user-images.githubusercontent.com/80379828/112961643-23f08380-9178-11eb-8bc6-4f5ea16a4d4a.png "obs num distribution")

### Average distance between obstacles
We set distance between adjacent obs according to their speeds and obs num.
![](https://latex.codecogs.com/svg.image?D_{obs}=max(D_{safe},&space;\frac{200}{obs_{num}}&plus;U(-4,&space;4)))


### Lane num
Currently we only consider 2 lane.
### Lane change direction
Currently, we only consider lane change left.

## Vehicle action

* Increase velocity control accuracy and speed range.
* Disable front obs lane change when ego car do a lane change.

### Increase velocity control accuracy and speed range
For convenience， we use a MDP-Vehicle model with a specified discrete range of allowed target speeds which use a high leve which use a high level action.
The action space consists of Faster, Slower, IDLE, Left lane change, Right lane change. And the discrete target speed is defined as 
![](https://latex.codecogs.com/svg.image?V_{target}=V_{min}&plus;V_{index}*\frac{(V_{max}-V_{min})}{V_{count}-1). The default 
![](https://latex.codecogs.com/svg.image?V_{max}=30)
![](https://latex.codecogs.com/svg.image?V_{min}=20)
![](https://latex.codecogs.com/svg.image?V_{count}=3)
For a accuracy speed control, we set  

![](https://latex.codecogs.com/svg.image?V_{min}=0) 

![](https://latex.codecogs.com/svg.image?V_{count}=19)
So, the default config has 2 target speed in average 10m/s, and current config has 6 target speed in average 10m/s.

And the target and real speed fig of above configs are shown as
![default target_real_v](https://user-images.githubusercontent.com/80379828/112982037-8fdde680-918e-11eb-9a02-ce84d1ef6378.png "default target_real_v")
![target_real_v](https://user-images.githubusercontent.com/80379828/112983079-cd8f3f00-918f-11eb-9525-5fe01a864693.png "target_real_v")

So, current config will may have a high variance and a low error due to the easy changeable target velocity. If we have a big difference between target and current speed, it will increase the comfort cost.


And the other config are setting as default as 
![](https://latex.codecogs.com/svg.image?a_{max}=5)

![](https://latex.codecogs.com/svg.image?a_{min}=-5)

![](https://latex.codecogs.com/svg.image?h_{min}=-pi/2)

![](https://latex.codecogs.com/svg.image?h_{max}=-pi/2)

#### Disable front obs lane change when ego car do a lane change
![rule_based_1](https://user-images.githubusercontent.com/80379828/112783501-09d47980-9082-11eb-9a26-f211209a4b09.gif)
![12](https://user-images.githubusercontent.com/80379828/113014496-3639e400-91af-11eb-851a-7697bdb8ce93.gif)

All obstacles are IDMVehicle models and would lane change if a rear vehicle cut in its lane. And this motion will change the lane change scenario and are abnormal in relistic environment. So we disable the obstacle lane change motion if it is caused by ego car.

### Control
Use a simple PP controler to control v and s.
## Rule-based method
We construct rule-based methods according to 
[window_selection.pdf](https://github.com/zhen-liu-github/high_env_simulator/files/6230431/window_selection.pdf). And the lane change time and success rate are shown as 

|obs_num | sample num | lane change time |lane change success rate|
|----|----|----|----|
| 1      |   4        |   3.25               |  100%|
 |2 | 32    | 5.15 | 87.5%|
|  3 |  108 | 5.46 | 90.74%|
|4  |  250 |  5.49  |94% |
|5 |  271 |  5.50   |   92.62%|
|6| 137| 5.14   | 94.89%|
|7| 51|  5.42    | 94.12%|
|8| 15| 6.8    | 93.33%|
|9| 4|   2.90   | 100% |
|overall| 874 | 5.46 | 92.67%|

126/1000 crashed.
![1](https://user-images.githubusercontent.com/80379828/113030159-df88d600-91bf-11eb-8bcd-3fecd256c508.gif)
The yellow window is the target window with the minimum chasing window time.

issue:
* Weak control capability
* Trade-off between saftey-check and lat lane change motion.
* No collision check

## Data-driven
We construct a simple model to infer window confidence. The model structure is defined as :
### Model structure
![model structure](https://user-images.githubusercontent.com/80379828/113032811-de0cdd00-91c2-11eb-94df-b147f3bc4587.png "model structure")
![data_driven](https://user-images.githubusercontent.com/80379828/112783107-199f8e00-9081-11eb-91e4-5f5a6898edb3.gif)
### Feature
We only concat features of ego car and obs to get a 12-dimension window-feature including x, y, vx, vy, hx, hy.
Currently, the model's performance is not stable and have a high crash rate.
![data_driven](https://user-images.githubusercontent.com/80379828/112783107-199f8e00-9081-11eb-91e4-5f5a6898edb3.gif)

The yellow window is the target window with the highest window confidence and blue windows are all feasible lane change window.
(The train dataset comes from rule-based window selection simulations.)
|obs_num | sample num | lane change time |lane change success rate|
|----|----|----|----|
| 1      |   6        |   9.4               |  0.6667|
 |2 | 27    | 6.58 |0.4815|
|  3 |  97 | 6.24 | 0.7112|
|4  |  257 |  5.3  |0.7393 |
|5 |  292 |   6.38 |   0.7192|
|6| 139| 7.18   | 0.61115|
|7| 51| 7.69   | 0.4792|
|8| 7|   6.67 | 0.4286|
|9| 2|   6   | 0.5 |
|10| 1|   7   | 1 |
|overall| 879 | 6.78 | 0.7153|
121/1000 crashed
* Need feature engeering
* Solve overfitting.
* Wrong case analysis
# run script with rule-based window selection.
python model_test.py --type rule-based





# run script with data-driven window selection.

python model_test.py --type data-driven



