# high_env_simulator

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
