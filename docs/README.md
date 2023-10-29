# Klipper Advanced Logging Extension (KALE)

## 1. Product Vision

**Product Name:** Klipper Advanced Logging Extension (KALE)

**Vision Statement:** 
To provide 3D printing enthusiasts and professionals with an advanced logging application that integrates seamlessly with existing Klipper interfaces, offering detailed insights into each print job.

## 2. User Stories

Main functionalities:

- **As a** 3D printer user, **I want** to see a record of all my print jobs, **so that** I can refer back to them at any time.
- **As a** 3D printer user, **I want** to view the start and end times of each job, **so that** I can track how long each print takes.
- **As a** 3D printer user, **I want** to see a 3D plot of bed mesh leveling for each job, **so that** I can ensure consistent printing quality.
- **As a** 3D printer user, **I want** to view accelerometer data, **so that** I can diagnose potential issues or optimize my prints.
- **As a** 3D printer user, **I want** to see the power drawn by stepper motors, **so that** I can ensure they are functioning correctly.
- **As a** 3D printer user, **I want** to view average speeds for infill and outer walls, **so that** I can optimize print time and quality.
- **As a** 3D printer user, **I want** the app to run alongside Fluidd or Mainsail, **so that** I can have a centralized platform for managing and monitoring my prints.

## 3. Prioritization

MoSCoW method:

- **Must have:** Records of all print jobs, start/end times, compatibility with Fluidd or Mainsail.
- **Should have:** 3D plot of bed mesh leveling, accelerometer data.
- **Could have:** Stepper motor power data, avg speeds for infill and outer walls.
- **Won't have this time:** Any additional features thought of later. They can be considered in future sprints.

## 4. Estimation

Agile story points for estimation. For simplicity:

- 1 point: 1 day
- 2 points: 2-3 days
- 3 points: A week
... and so on.

## 5. Sprint Planning

For the first sprint, focus on the "Must have" features. Depending on capacity (individual or team), choose the number of stories believed to be completable in a sprint (typically 2 weeks).

## 6. Design and Architecture

Before starting the sprints, consider the overall architecture of the app. Since it will run alongside Fluidd or Mainsail, an API layer (perhaps leveraging Moonraker) and a database to store the job logs will likely be needed.

## 7. Tools & Tech Stack

- **Backend:** Python 3.9
- **Database:** SQLite
- **Frontend:** Lightweight framework that can integrate into Fluidd or Mainsail.
