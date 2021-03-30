# high_env_simulator
This repository is based on the [Highway-env](https://github.com/eleurent/highway-env) and aims to compare different lane change method's performances.

## Env config.
The env distribution of the simulator will affect the mothod performance. And a perfect simulator has a realistic env and can focus on the difficult part. 
Currently, speed distribution of ego car and obstacles, obstacles num, average distance between obstacles, lane num, lane change direction and so on.

### Speed distribution
The speed of ego car and lane change window have a huge impact on lane change motion. A typically overall speed distribution is seems like the following.

![speed distribution fig](https://user-images.githubusercontent.com/80379828/112944678-bc313d00-9165-11eb-8dcc-774b3eb8bac2.png "speed_distribution_fig")

Firstly, we random sample ego speed 
![](http://latex.codecogs.com/svg.latex?V_{ego})
and obs speed 
![](http://latex.codecogs.com/svg.latex?V_{obs})
For each obs speed, we sampele the velocity 
![](http://latex.codecogs.com/svg.latex?V_{0bs_i})
from a narrow norm distribution with loc=
![](http://latex.codecogs.com/svg.latex?V_{obs_i})
scale = 
![](http://latex.codecogs.com/svg.latex?V_{obs_i}^{0.5})

![A toy obstacles example with 30 overall obs speed](https://user-images.githubusercontent.com/80379828/112946500-2945d200-9168-11eb-8561-372a8a97effe.png "an obs speed distribution")

### Obs num
The more obstacles, the more difficult to lane change. To ensure a relistic and difficult lane change scenario, we set 
![](https://latex.codecogs.com/svg.image?N_{obs}=Int(N(8,&space;2))&space;)
![obs num distribution](https://user-images.githubusercontent.com/80379828/112948233-67dc8c00-916a-11eb-9893-f0c6059ee206.png "obs num distribution")

### Average distance between obstacles
We set distance between adjacent obs according to their speeds and obs num.
![](http://latex.codecogs.com/svg.latex?D_{obs}=max(D_{safe}, 200/obs_num+U(-4,4)))

# run script with rule-based window selection.
python model_test.py --type rule-based
![rule-based](https://user-images.githubusercontent.com/80379828/112783305-a0546b00-9081-11eb-8bf8-17dbbe4ce476.gif)
![rule_based_1](https://user-images.githubusercontent.com/80379828/112783501-09d47980-9082-11eb-9a26-f211209a4b09.gif)

The yellow window is the target window with the minimum chasing window time.



# run script with data-driven window selection.

python model_test.py --type data-driven
![data_driven](https://user-images.githubusercontent.com/80379828/112783107-199f8e00-9081-11eb-91e4-5f5a6898edb3.gif)

The yellow window is the target window with the highest window confidence and blue windows are all feasible lane change window.
(The train dataset comes from rule-based window selection simulations.)
