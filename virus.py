import dataclasses
import random
from typing import ClassVar, Generator, NamedTuple

random.seed(40351)

@dataclasses.dataclass
class Employee:
    virus_receive_count: int = 0
    identifier: int = -1
    __next_id: ClassVar[int] = 0

    def __post_init__(self) -> None:
        if self.identifier < 0:
            self.identifier = self.__class__.__next_id
            self.__class__.__next_id += 1
            pass


class Count(NamedTuple):
    uninfected: int
    spreader: int
    immune: int
    ever_infected: int


class Corporation:
    def __init__(
        self,
        size: int
    ) -> None:
        self.size = size
        self.employee_map = {
            number: Employee(identifier=number)
            for number
            in range(self.size)
        }
        self.simulation_day = 0

        # Infect one employee.
        # Make it employee 0, without loss of generality
        self.employee_map[0].virus_receive_count = 1

    def get_counts(self) -> Count:
        uninfected_count = 0
        spreader_count = 0
        immune_count = 0
        ever_infected_count = 0
        for employee in self.employee_map.values():
            if employee.virus_receive_count == 0:
                uninfected_count += 1
            elif employee.virus_receive_count == 1:
                spreader_count += 1
                ever_infected_count += 1
            else:
                immune_count += 1
                ever_infected_count += 1
        return Count(uninfected_count, spreader_count, immune_count, ever_infected_count)

    def uninfected_employees(self) -> Generator[tuple[int, Employee], None, None]:
        return (
            (id, employee)
            for (id, employee)
            in self.employee_map.items()
            if employee.virus_receive_count == 1
        )

    def spreader_employees(self) -> Generator[tuple[int, Employee], None, None]:
        return (
            (id, employee)
            for (id, employee)
            in self.employee_map.items()
            if employee.virus_receive_count == 1
        )

    def immune_employees(self) -> Generator[tuple[int, Employee], None, None]:
        return (
            (id, employee)
            for (id, employee)
            in self.employee_map.items()
            if employee.virus_receive_count > 2
        )


    def tick(self):
        """Advance the simulation by one day"""
        # Send emails
        for (id, employee) in self.spreader_employees():
            # Send 3 emails
            for _ in range(3):
                # Only 40% of emails will be infected 
                if random.random() > 0.4:
                    continue

                # Choose a random employee who is not themself
                target_id = id
                while target_id == id:
                    target_id = random.randrange(self.size)
                target_employee = self.employee_map[target_id]

                # Send the infected email
                target_employee.virus_receive_count += 1

        # Advance the day
        self.simulation_day += 1


class Simulation:
    def __init__(
        self,
        size: int = 100,
        days: int = 10,
        sim_count: int = 1,
    ) -> None:
        self.size = size
        self.days = days
        self.sim_count = sim_count
        self.data: list[list[Count]] = []
        for sim_index in range(sim_count):
            # print(f"Running sim {sim_index + 1} of {self.sim_count}")
            self.run_data: list[Count] = []
            self.corp = Corporation(size=size)
            self.run_data.append(self.corp.get_counts())
            for day in range(days):
                self.corp.tick()
                self.run_data.append(self.corp.get_counts())
            self.data.append(self.run_data)

        # Average the data
        self.uninfected_average = [0.0 for _ in range(self.days + 1)]
        self.spreader_average = [0.0 for _ in range(self.days + 1)]
        self.immune_average = [0.0 for _ in range(self.days + 1)]
        self.ever_infected_average = [0.0 for _ in range(self.days + 1)]
        for run in self.data:
            (
                run_uninfected,
                run_spreader,
                run_immune,
                run_ever_infected
            ) = convert_to_percentage_lists(run)
            
            for index in range(self.days + 1):
                self.uninfected_average[index] += run_uninfected[index] / self.sim_count
                self.spreader_average[index] += run_spreader[index] / self.sim_count
                self.immune_average[index] += run_immune[index] / self.sim_count
                self.ever_infected_average[index] += run_ever_infected[index] / self.sim_count



def convert_to_percentage_lists(data: list[Count]):
    total_count = data[0].uninfected + data[0].spreader + data[0].immune
    uninfected = [
        point.uninfected / total_count
        for point
        in data
    ]
    spreader = [
        point.spreader / total_count
        for point
        in data
    ]
    immune = [
        point.immune / total_count
        for point
        in data
    ]
    ever_infected = [
        point.ever_infected / total_count
        for point
        in data
    ]
    return (uninfected, spreader, immune, ever_infected)

if __name__ == "__main__":
    # corp = Corporation(10000)
    # print(corp.employee_map)
    # print(corp.simulation_day, corp.get_counts())
    # for _ in range(100):
    #     corp.tick()
    #     print(corp.simulation_day, corp.get_counts())
    for size in [10, 100, 1000, 10000]:
        sim = Simulation(
            size=size, days=50, sim_count=100
        )
        # print(sim.run_data)
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax: plt.Axes

        (uninfected, spreader, immune, ever_infected) = convert_to_percentage_lists(sim.run_data)
        ax.plot(range(sim.days + 1), sim.uninfected_average, label="uninfected")
        # ax.plot(range(sim.days + 1), uninfected, label="uninfected")
        ax.plot(range(sim.days + 1), sim.spreader_average, label="spreader")
        ax.plot(range(sim.days + 1), sim.immune_average, label="immune")
        ax.plot(range(sim.days + 1), sim.ever_infected_average, label="ever_infected")
        ax.set_ylim(0, 1)
        ax.set_xlim(0, sim.days)
        ax.set_xlabel(f"Simulation day")
        ax.set_ylabel(f"Fraction")
        ax.legend()
        ax.set_title(f"company_size={sim.size:,}; sim_count={sim.sim_count:,}")
        plt.show()

        for n in [3, 20, 40]:
            print(f"N={sim.size:,}: Fraction infected after {n} days={sim.ever_infected_average[n + 1]:%}")

        found_10_percent = False
        found_50_percent = False
        for day, percentage in enumerate(sim.ever_infected_average):
            if not found_10_percent and percentage >= 0.10:
                found_10_percent = True
                print(f"N={sim.size:,}: 10% infected on day {day}")
            if not found_50_percent and percentage >= 0.50:
                found_50_percent = True
                print(f"N={sim.size:,}: 50% infected on day {day}")
