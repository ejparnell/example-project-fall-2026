# Pokémon TCG AI Battle Challenge: Strategy Category

**Company / Org:** Pokémon TCG AI Battle Challenge  
**Challenge Advisors:** Professor Oak and Professor Elm *(fictional)*  
**AI Studio Coach:** Professor Juniper *(fictional)*  
**Program:** Break Through Tech AI Studio - Fall 2026  

> **Example project note:** The Pokémon TCG challenge is real, but this repository is a fictional example of the GitHub project space expected for AI Studio. The team members, Challenge Advisors, and coach are invented Pokémon-themed participants used to demonstrate Issues, milestones, ownership, and documentation.

---

## 🏢 About the Challenge

The Pokémon Trading Card Game (TCG) is a strategic game in which successful play depends on deck construction, decision-making, matchup awareness, and adaptation to changing game conditions. The Pokémon TCG AI Battle Challenge asks participants to develop AI Training Agents that can compete in this dynamic environment and to explain the strategic reasoning behind their systems.

The Strategy Category runs alongside the Simulation Category. While the Simulation Category evaluates an agent's win rate and performance, the Strategy Category evaluates the logic behind the agent: why a strategy was selected, which hypotheses were tested, and how the design reflects an understanding of the game's mechanics and structure.

---

## 🎯 The Challenge

### Project Summary

The example team will design, test, and document an AI Training Agent for the Pokémon TCG. The project should explore methods for improving agent performance under dynamic gameplay conditions while making the agent's strategy understandable to others.

The work should address more than leaderboard optimization. The example team is expected to make intentional choices about deck construction, compare multiple strategies, test strength across matchups, and evaluate whether the agent can perform consistently over repeated games. Deep analysis, originality, and clear reporting are important even when an agent does not finish near the top of the leaderboard.

The project team is represented in the [README](README.md) by Ash Ketchum, Misty Williams, Brock Harrison, Erika Otsuka, and Gary Oak. All are fictional examples.

> **Participation requirement:** A complete competition entry requires participation in both the Simulation Category and the Strategy Category. The strategic analysis in this project should therefore be grounded in an agent developed and evaluated in the simulation environment.

### Success Criteria

Submissions are evaluated across three areas:

| Category | Weight | What Success Looks Like |
|---|---:|---|
| **Model Score** | **70%** | The approach and rationale are clearly explained; the methods are original and technically sound; the model performs consistently across repeated matches; the strategy does not over-rely on favorable initial states or specific matchups; and the agent performs competitively within its track. |
| **Deck Score** | **20%** | The deck concept is clearly explained and aligned with the intended strategy, and key cards are selected and used effectively to support the game plan. |
| **Report Score** | **Not shown in source brief** | The report is logical, clear, and well structured, with figures, charts, tables, or other visuals used effectively to support the analysis. |

> **Weight confirmation:** The supplied brief assigns 70% to Model Score and 20% to Deck Score but omits the visible Report Score weight. If the categories total 100%, the implied remainder is 10%; confirm this on the competition page before submission.

A successful project will include:

- A working AI Training Agent entered in the Simulation Category.
- A deliberate deck concept connected to the agent's strategic logic.
- Repeated-match evaluation and matchup analysis.
- Clearly stated hypotheses, experiments, results, and limitations.
- A polished strategy report that another team can understand and learn from.

### Project Milestones

Use one native GitHub milestone per monthly outcome. Only the active month receives Issues; the
Project's `Target Cycle` iteration field carries weekly sequencing.

| Month | Milestone | Key Activities |
|---|---|---|
| **September** | September Baseline | Freeze the Authoritative Source, implement a deterministic rule-based agent and Reference Deck, complete 20 real CABT matches, and independently verify a versioned Artifact Bundle. |
| **October** | October Analysis | Analyze match logs and available feedback, calculate matchup-level performance, document failed approaches, and test whether conclusions survive repeated trials. |
| **November** | November Refinement | Compare the baseline with an evidence-supported improvement, stress-test assumptions, and refine reproducibility evidence. |
| **December** | December Portfolio | Turn the accepted work into a clear portfolio narrative, finalize visualizations and limitations, and prepare the final presentation. |

---

## 📊 Dataset

**Name and Source:** Pokémon TCG AI Battle Challenge card metadata and reference materials  
**Format:** CSV and PDF  
**Location:** [data/pokemon-tcg-ai-battle-challenge-strategy](data/pokemon-tcg-ai-battle-challenge-strategy)  

### Key Details

- The dataset maps simulator card IDs to card names, expansions, collection numbers, types, rules, attacks, and other gameplay metadata.
- English and Japanese card metadata are provided. The underlying card pool is the same across both languages.
- English and Japanese PDF reference documents include the card IDs and card images used in the competition environment.
- See the [data guide](data/README.md) for the complete file inventory, schema, and notes about the supplied alternate exports.

---

## 🛠️ Suggested Approach

**ML Problem Type:** Sequential decision-making under partial observability, game AI, and empirical strategy evaluation  

**Algorithm Examples:** Rule-based or heuristic policies as a baseline; search-based planning; and reinforcement-learning policies as an evidence-supported extension  

**Recommended Libraries and Tools:** Pokémon TCG battle simulator SDK, `kaggle-environments`, Python, pandas, NumPy, Matplotlib or Seaborn, and optionally PyTorch/TorchRL  

**Evaluation Metrics:** Competition skill rating; overall and matchup-level win rate; uncertainty or confidence intervals; failed/invalid episode rate; repeated-run stability; and the Model, Deck, and Report rubric criteria  

1. **Understand the card pool** — Load the frozen English export through the Catalog, validate
   its schema and hash, and connect simulator card IDs to human-readable Card Records.
2. **Establish the integration baseline** — Hold the official sample deck constant and compare the
   transparent Baseline Agent with a first-legal Integration Control.
3. **Produce trustworthy evidence** — Run 20 CABT matches from an identified commit, balance both
   player positions, and retain structured results, provenance, interpretation, and limitations.
4. **Evaluate robustness later** — Use the accepted September bundle to design October matchup and
   failure analysis without retroactively tuning the baseline.
5. **Refine the agent and deck together** — Use experimental evidence to improve both gameplay decisions and deck construction.
6. **Document the reasoning** — Turn the experiment history into a clear report explaining the final model, deck, results, and limitations.

**Evaluation Focus:** Repeated-match performance, stability, matchup robustness, strategic originality, deck-strategy alignment, and clarity of reporting.

---

## 📝 Submission Requirements

The final Strategy Category submission must be made before the deadline and must contain a submitted Kaggle Writeup. Draft or unsubmitted writeups are not considered by the judges.

### Kaggle Writeup

- Include a title, subtitle, and detailed analysis of the submission.
- Select a competition track before submitting.
- Keep the writeup at or below **2,000 words**; longer submissions may be penalized.
- Code repositories, Kaggle notebooks, and external links may be attached.

### Media Gallery (Optional)

Images or videos may be attached to the writeup, provided that all content complies with the competition's license terms. Submissions containing images that violate the license granted for Pokémon elements will not be evaluated and may be disqualified.

> **Publication note:** A private Kaggle resource attached to a public writeup will automatically become public after the competition deadline.

---

## 📚 Resources to Get Started

**Competition and Simulator:**

- [Pokémon TCG AI Battle Challenge Simulation overview](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/overview)
- [cabt simulator API documentation](https://matsuoinstitute.github.io/cabt/)
- [Kaggle Environments repository](https://github.com/Kaggle/kaggle-environments)
- [Local card-data guide](data/README.md)

**Technical Tutorials:**

- [PyTorch reinforcement-learning tutorial](https://docs.pytorch.org/tutorials/intermediate/reinforcement_q_learning.html)
- [Gymnasium environment-design guide](https://gymnasium.farama.org/main/introduction/create_custom_env/)

Start with a transparent heuristic policy and reliable experiment harness. Adopt reinforcement learning only after the team can reproduce the baseline and define a measurable reason for the added complexity.

---

## 🤝 How We'll Work Together

**Official check-ins:** Fictional biweekly check-ins with Professor Oak and Professor Elm  
**Communication:** Fictional team-and-advisor channel  
**Response time:** Fictional 48-hour weekday response target  

**Recommended Tools:**

- **Coding and experiments:** Google Colab, Kaggle Notebooks, or VS Code
- **Collaboration and task planning:** GitHub and GitHub Projects
- **Simulation:** Official competition simulator SDK and local match logs
- **Meetings:** Zoom or Google Meet

---

## 🚀 Getting Started

1. **Review this overview** and identify questions about the competition, simulator, or evaluation rubric.
2. **Read the [data guide](data/README.md)** and inspect the English card metadata.
3. **Run the [Getting Started](Getting-Started-for-Fellows.md) checks** before changing code or data.
4. **Use the [September delivery plan](docs/project/september-baseline.md)** to create the milestone,
   five dependent Issues, Project fields, and saved views.

---

## ❓ Questions?

Bring questions about the competition requirements, simulator access, team workflow, or project scope to the first AI Studio meeting with the fictional project staff. These names and roles are examples only and do not represent real people or organizations.
