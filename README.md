# Sky-Drive

> [!IMPORTANT]
> We are currently in the process of organizing our code, and will release the code on GitHub in the near future.
>
> 🫶 Stay up to date at this repository and the [Sky-Lab](https://sky-lab-uw.github.io/) website!

<div align="center">
  <div>
<h2 style="
  display:inline-flex;
  align-items:center;
  gap:12px;
  margin:0;
">
  <img src="Sky-Drive.png" width="45" alt="Sky-Drive logo" style="vertical-align:middle;">
  Sky-Drive: A Distributed Multi-Agent Simulation Platform for Human-AI Collaborative and Socially-Aware Future Transportation
</h2>
	 <h5 style="margin:6px 0 0 0;">
      <em>(This paper was accepted by Journal of Intelligent and Connected Vehicles (JICV) in August, 2025)</em>
    </h5>
  </div>
  <h3 align="center"><a href="https://sky-lab-uw.github.io/Sky-Drive-website/">Website</a> | <a href="https://arxiv.org/abs/2504.18010">JICV</a> | <a href="https://arxiv.org/abs/2504.18010">arXiv</a> </h3>
</div>

<br/>

> **Sky-Drive: A Distributed Multi-Agent Simulation Platform for Human-AI Collaborative and Socially-Aware Future Transportation**
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
> <sup>*</sup>Equally Contributing First Authors,
> <sup>✉</sup>Corresponding Author
> <br/>

<img align="center" src="assets/fig1.svg" width="1100" alt="skydrive"/>

<p align="center" style="font-size:16px; font-weight:normal; margin-top:8px;">Overview of Sky-Drive’s key components and functionalities.</p>

## 📢 News

- **`[2025/11/19]`** 🎬 We uploaded the **video summary** of the paper.
- **`[2025/11/17]`** 🚀🚀 We released the code of **multi-agent architecture** and **accident scenario generation**.
- **`[2025/08/18]`** 🎉🎉 Sky-Drive has been accepted for publication in ***Journal of Intelligent and Connected Vehicles* (JICV)**!  We will release the website and related resources soon. Stay tuned!
- **`[2025/04/25]`** 🔥🔥 We released the first vision of **Sky-Drive** paper on arXiv!

## 💡 Highlights <a name="highlight"></a>

- **Sky-Drive** extends autonomous driving research beyond conventional safety and efficiency metrics, introducing a comprehensive framework for socially-aware and human-aligned autonomous behavior.
- This work addresses the critical challenge of modeling and understanding complex multi-agent interactions in mixed traffic environments, where heterogeneous intelligent agents must align with human preferences and societal norms.

## 🎬 Four Minutes Summary

https://github.com/user-attachments/assets/5f95beb4-b2a2-4d0f-95d3-079348076201

## 📋 Table of Contents

- [Sky-Drive](#sky-drive)
  - [📢 News](#-news)
  - [💡 Highlights ](#-highlights-)
  - [🎬 Four Minutes Summary](#-four-minutes-summary)
  - [🛠️ Getting Started ](#️-getting-started-)
  - [1️⃣ VR-based AV-HRU Interaction ](#️-VR-)
  - [2️⃣ HAIM-based Deep Reinforcement Learning ](#-HAIM-)
  - [3️⃣ Vision Language Model-Enabled Reinforcement Learning ](#-VLM-)
  - [4️⃣ Personalized Safety-Critical Curriculum Learning ](#-Curri-)
  - [5️⃣ Accident Data Replay ](#-Accident-)
  - [👥 Contributors ](#-contributors-)
  - [🎯 Citation ](#-citation-)
  - [📚 Other Resources ](#-other-resources-)

## 🛠️ Getting Started <a name="setup"></a>
To get started with Sky-Drive:

1. **Clone this repository**
   ```bash
   git clone https://github.com/BillWan-zzzyyy/Sky-Drive.git
   cd Sky-Drive
   ```

2. **Download and install CARLA 0.9.13**

   - Download CARLA 0.9.13 from the [official release page](https://github.com/carla-simulator/carla/releases/tag/0.9.13).
   
     Example (for standard Linux version):
     ```bash
     wget https://carla-releases.s3.eu-west-3.amazonaws.com/Linux/CARLA_0.9.13.tar.gz
     tar -xvzf CARLA_0.9.13.tar.gz
     ```

   - If you want to use VR features, you need to install the ***build version*** of CARLA 0.9.13 with Unreal Engine 4.26.  
     Please refer to [build instructions](https://carla.readthedocs.io/en/latest/build_carla/) and the [official CARLA documentation](https://carla.readthedocs.io/en/latest/) for setup and further details.

3. **Refer to the relevant sections/folders for feature usage.**


> ⚡️ **Recommended Environment:**  
> - **Ubuntu 20.04**  
> - **Python 3.7+**  
> - **CARLA 0.9.13**  
>
> ⚠️ *Note: While most features may work with other CARLA versions, for **VR and Multi-agent support**, CARLA 0.9.13 is strongly recommended!*


## 🚶‍♀️ Multi-agent Architecture <a name="Multi-agent"></a>

https://github.com/user-attachments/assets/10c0ff95-7f50-4272-87c9-ee69b5820cef

## 📊 Evaluation <a name="evaluation"></a>

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
                    <img src="https://sky-lab-uw.github.io/assets/img/group-members/group_yuhao.jpg" width="100;" alt="yuhaoluo"/>
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

## 🎯 Citation <a name="citation"></a>

If you find **Sky-Drive** useful for your research, you are more than welcome to give us a star 🌟 and citing our paper:

```BibTeX
@article{huang2025sky,
  title={Sky-Drive: A Distributed Multi-Agent Simulation Platform for Human-AI Collaborative and Socially-Aware Future Transportation},
  author={Huang, Zilin and Sheng, Zihao and Wan, Zhengyang and Qu, Yansong and Luo, Yuhao and Wang, Boyue and Li, Pei and Chen, Yen-Jung and Chen, Jiancong and Long, Keke and others},
  journal={arXiv preprint arXiv:2504.18010},
  year={2025}
}
```

<p align="right">(<a href="#top">back to top</a>)</p>

## 📚 Other Resources <a name="resources"></a>

Our team at Sky-Lab is actively working on research projects in the field of AI and autonomous driving. Here are a few of them you might find interesting:

- **[VLM-RL for Safe Autonomous Driving](https://github.com/zihaosheng/VLM-RL)**
- **[Human as AI mentor](https://zilin-huang.github.io/HAIM-DRL-website/)**
- **[Physics-enhanced RLHF](https://zilin-huang.github.io/PE-RLHF-website/)**
- **[LLM for for Interactive and Traffic Scenario Generation](https://github.com/zihaosheng/Talk2Traffic)**
- **[Traffic expertise meets residual RL](https://github.com/zihaosheng/traffic-expertise-RL)**
- **[LLMs for Traffic Accident Understanding](https://arxiv.org/abs/2508.06763)**

<p align="right">(<a href="#top">back to top</a>)</p>
