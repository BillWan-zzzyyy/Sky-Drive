# Sky-Drive
<div id="top" align="center">
<p align="center">
  <strong>
    <img src="Sky-Drive.png" width="60;" alt="boyuewang"/><h2 align="left">Sky-Drive: A Distributed Multi-Agent Simulation Platform for Human-AI Collaborative and Socially-Aware Future Transportation</h2>
    <h3 align="center"><a href="https://sky-lab-uw.github.io/Project%20SkyDrive/">Website</a> | <a href="https://arxiv.org/abs/2504.18010">arXiv</a> | <a href="https://sky-lab-uw.github.io/">Lab Website</a></h3>
  </strong>
</p>
</div>

<br/>

> **[Sky-Drive: A Distributed Multi-Agent Simulation Platform for Human-AI Collaborative and Socially-Aware Future Transportation](https://arxiv.org/html/2504.18010v2)**
>
> [Zilin Huang](https://scholar.google.com/citations?user=RgO7ppoAAAAJ&hl=en)<sup>1,\*</sup>,
> [Zihao Sheng](https://scholar.google.com/citations?user=3T-SILsAAAAJ&hl=en)<sup>1,\*</sup>,
> [Zhengyang Wan](https://scholar.google.com.hk/citations?user=6m8LnLUAAAAJ&hl=en)<sup>1,*</sup>,
> [Yansong Qu](https://scholar.google.com/citations?view_op=list_works&hl=zh-CN&user=hIt7KnUAAAAJ)<sup>2</sup>,
> [Yuhao Luo](https://scholar.google.com/citations?user=CNdSjWAAAAAJ&hl=en)<sup>1</sup>,
> [Boyue Wang](https://scholar.google.com/citations?user=CR7HWjcAAAAJ&hl=en)<sup>1</sup>,
> [Pei Li](https://scholar.google.com/citations?user=0QzhzL0AAAAJ&hl=en)<sup>1</sup>,
> [Yen-Jung Chen](https://scholar.google.com/citations?user=RZiRdWYAAAAJ&hl=en)<sup>2</sup>,
> [Jiancong Chen](https://scholar.google.com/citations?user=qa_mJTUAAAAJ&hl=en)<sup>2</sup>,
> [Keke Long](https://scholar.google.com/citations?user=zcTxZZ8AAAAJ&hl=en)<sup>1</sup>,
> [Jiayi Meng](https://scholar.google.com/citations?user=IlZs8_oAAAAJ&hl=en)<sup>3</sup>,
> [Yue Leng](https://scholar.google.com/citations?user=kEpj_AsAAAAJ&hl=en)<sup>4</sup>,
> [Sikai Chen](https://scholar.google.com/citations?user=DPN2wc4AAAAJ&hl=en)<sup>1,✉</sup><br>
>
> <sup>1</sup>University of Wisconsin-Madison, <sup>2</sup>Purdue University, <sup>3</sup>The University of Texas at Arlington, <sup>4</sup>Google
>
> <sup>\*</sup>Equally Contributing First Authors,
> <sup>✉</sup>Corresponding Author
> <br/>

## 📢 News
- **2025.08**: 🔥🔥 **Sky-Drive** has been accepted for publication in *Journal of Intelligent and Connected Vehicles*!  
  We will release the website and related resources soon. Stay tuned!

## 🎯 Citation <a name="citation"></a>

If you find **Sky-Drive** useful for your research, you are more than welcome to give us a star 🌟 and citing our paper:

```BibTeX
@article{huang2025sky,
  title={Sky-Drive: A Distributed Multi-Agent Simulation Platform for Human-AI Collaborative and Socially-Aware Future Transportation},
  author={Huang, Zilin and Sheng, Zihao and Wan, Zhengyang and Qu, Yansong and Luo, Yuhao and Wang, Boyue and Li, Pei and Chen, Yen-Jung and Chen, Jiancong and Long, Keke and others},
  journal={arXiv preprint arXiv:2504.18010
        
        
        
        
        
        
        
        },
  year={2025}
}
```

<p align="right">(<a href="#top">back to top</a>)</p>

## 💡 Highlights <a name="highlight"></a>

🔥 To the best of our knowledge, **VLM-RL** is the first work in the autonomous driving field to unify VLMs with RL for
end-to-end driving policy learning in the CARLA simulator.

🏁 **VLM-RL** outperforms state-of-the-art baselines, achieving a 10.5% reduction in collision rate, a 104.6% increase in
route completion rate, and robust generalization to unseen driving scenarios.

## 📋 Table of Contents

1. [Highlights](#highlight)
2. [Getting Started](#setup)
3. [Training](#training)
4. [Evaluation](#evaluation)
5. [Contributors](#contributors)
6. [Citation](#citation)
7. [Other Resources](#resources)

## 🛠️ Getting Started <a name="setup"></a>


1. Download and install `CARLA 0.9.13` from the [official release page](https://github.com/carla-simulator/carla/releases/tag/0.9.13).
2. Create a conda env and install the requirements:
```shell
# Clone the repo
git clone https://github.com/zihaosheng/VLM-RL.git
cd VLM-RL

# Create a conda env
conda create -y -n vlm-rl python=3.8
conda activate vlm-rl

# Install PyTorch
pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu116

# Install the requirements
pip install -r requirements.txt
```

3. Start a Carla server with the following command. You can ignore this if `start_carla=True`

```shell
./CARLA_0.9.13/CarlaUE4.sh -quality_level=Low -benchmark -fps=15 -RenderOffScreen -prefernvidia -carla-world-port=2000
```

If `start_carla=True`, revise the `CARLA_ROOT` in `carla_env/envs/carla_route_env.py` to the path of your CARLA installation.

<p align="right">(<a href="#top">back to top</a>)</p>

## 🚋 Training <a name="training"></a>

### Training VLM-RL

To reproduce the results in the paper, we provide the following training scripts:

```shell
python train.py --config=vlm_rl --start_carla --no_render --total_timesteps=1_000_000 --port=2000 --device=cuda:0
```

**Note:** On the first run, the script will automatically download the required OpenCLIP pre-trained model, which may take a few minutes. Please wait for the download to complete before the training begins.

#### To accelerate the training process, you can set up multiple CARLA servers running in parallel. 
<details>
  <summary>For example, to train the VLM-RL model with 3 CARLA servers on different GPUs, run the following commands in three separate terminals:
</summary>

#### Terminal 1:
```shell
python train.py --config=vlm_rl --start_carla --no_render --total_timesteps=1_000_000 --port=2000 --device=cuda:0
```

#### Terminal 2:
```shell
python train.py --config=vlm_rl --start_carla --no_render --total_timesteps=1_000_000 --port=2005 --device=cuda:1
```

#### Terminal 3:
```shell
python train.py --config=vlm_rl --start_carla --no_render --total_timesteps=1_000_000 --port=2010 --device=cuda:2
```
</details>

To train the VLM-RL model with PPO, run:
```shell
python train.py --config=vlm_rl_ppo --start_carla --no_render --total_timesteps=1_000_000 --port=2000 --device=cuda:0
```

### Training Baselines

To train baseline models, simply change the `--config` argument to the desired model. For example, to train the TIRL-SAC model, run:
```shell
python train.py --config=tirl_sac --start_carla --no_render --total_timesteps=1_000_000 --port=2000 --device=cuda:0
```

More baseline models can be found in the `CONFIGS` dictionary of `config.py`.

<p align="right">(<a href="#top">back to top</a>)</p>

## 📊 Evaluation <a name="evaluation"></a>

To evaluate trained model checkpoints, run:

```shell
python run_eval.py
```

**Note:** that this command will first **KILL** all the existing CARLA servers and then start a new one. 
Try to avoid running this command while training is in progress.

<p align="right">(<a href="#top">back to top</a>)</p>

## 👥 Contributors <a name="contributors"></a>

Special thanks to the following contributors who have helped with this project:

<!-- readme: contributors -start -->
<table>
	<tbody>
		<tr>
			<td align="center">
                <a href="https://github.com/zilin-huang">
                    <img src="https://avatars.githubusercontent.com/u/59532565?v=4" width="100;" alt="zilinhuang"/>
                    <br />
                    <sub><b>Zilin Huang</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://github.com/zihaosheng">
                    <img src="https://scholar.googleusercontent.com/citations?view_op=view_photo&user=3T-SILsAAAAJ&citpid=7" width="100;" alt="zihaosheng"/>
                    <br />
                    <sub><b>Zihao Sheng</b></sub>
                </a>
            </td>
			<td align="center">
                <a href="https://github.com/BillWan-zzzyyy">
                    <img src="https://scholar.googleusercontent.com/citations?view_op=view_photo&user=6m8LnLUAAAAJ&citpid=18" width="100;" alt="zhengyangwan"/>
                    <br />
                    <sub><b>Zhengyang Wan</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://scholar.google.com/citations?user=hIt7KnUAAAAJ&hl=en&oi=sra">
                    <img src="https://scholar.googleusercontent.com/citations?view_op=view_photo&user=hIt7KnUAAAAJ&citpid=2" width="100;" alt="yansongqu"/>
                    <br />
                    <sub><b>Yansong Qu</b></sub>
                </a>
            </td>
			</td>
            <td align="center">
                <a href="https://scholar.google.com/citations?user=CNdSjWAAAAAJ&hl=en">
                    <img src="https://scholar.googleusercontent.com/citations?view_op=view_photo&user=CNdSjWAAAAAJ&citpid=2" width="100;" alt="yuhaoluo"/>
                    <br />
                    <sub><b>Yuhao Luo</b></sub>
                </a>
            </td>
	        <td align="center">
                <a href="https://scholar.google.com/citations?user=CR7HWjcAAAAJ&hl=zh-CN">
                    <img src="https://sky-lab-uw.github.io/assets/img/group-members/group_boyue.jpg" width="100;" alt="boyuewang"/>
                    <br />
                    <sub><b>Boyue Wang</b></sub>
                </a>
            </td>
		</tr>
	<tbody>
</table>
<!-- readme: contributors -end -->

<p align="right">(<a href="#top">back to top</a>)</p>


## 📚 Other Resources <a name="resources"></a>

Our team is actively working on research projects in the field of AI and autonomous driving. Here are a few of them you might find interesting:

- **[VLM-RL for Safe Autonomous Driving](https://github.com/zihaosheng/VLM-RL)**
- **[Human as AI mentor](https://zilin-huang.github.io/HAIM-DRL-website/)**
- **[Physics-enhanced RLHF](https://zilin-huang.github.io/PE-RLHF-website/)**
- **[LLM for for Interactive and Traffic Scenario Generation](https://github.com/zihaosheng/Talk2Traffic)**
- **[Traffic expertise meets residual RL](https://github.com/zihaosheng/traffic-expertise-RL)**
  
<p align="right">(<a href="#top">back to top</a>)</p>
