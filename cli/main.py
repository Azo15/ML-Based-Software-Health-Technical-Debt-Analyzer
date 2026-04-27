"""
Command Line Interface for the ML-Based Software Health & Technical Debt Analyzer.
Uses Typer for a modern and readable terminal experience.
"""
import typer
import os
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from data_collector.git_miner import GitMiner
from feature_extractor.metrics_analyzer import MetricsAnalyzer
from model.debt_estimator import DebtEstimator
from utils.logger import logger

app = typer.Typer(help="ML-Based Software Health & Technical Debt Analyzer CLI")
console = Console()

@app.command()
def analyze(
    repo_path: str = typer.Argument(..., help="Path to the local repository or remote URL"),
    max_commits: int = typer.Option(50, "--max-commits", "-m", help="Maximum number of commits to mine"),
    file_path: Optional[str] = typer.Option(None, "--file", "-f", help="Specific file to analyze (relative to repo path)")
):
    """
    Analyzes a Git repository, trains a model on bug-fix data, and estimates
    Technical Debt and Health Score for the codebase.
    """
    console.print(Panel.fit("[bold blue]ML-Based Software Health & Technical Debt Analyzer[/bold blue]", border_style="blue"))
    
    try:
        # Step 1: Mine Git Repo
        logger.info("[bold]Phase 1: Mining Git Repository[/bold]", extra={"markup": True})
        miner = GitMiner(repo_path)
        raw_data = miner.mine_commits(max_commits=max_commits)
        
        if not raw_data:
            logger.error("No Python file modifications found in the mined commits.")
            raise typer.Exit(code=1)

        # Step 2: Extract Features
        logger.info("[bold]Phase 2: Extracting Complexity Metrics[/bold]", extra={"markup": True})
        analyzer = MetricsAnalyzer()
        processed_data = []
        
        with console.status("[bold green]Calculating metrics...") as status:
            for item in raw_data:
                metrics = analyzer.analyze_code(item['source_code'])
                if metrics['loc'] > 0: # Only keep if there's actual code
                    item.update(metrics)
                    processed_data.append(item)
                
        logger.info(f"Successfully extracted metrics for {len(processed_data)} file revisions.")

        # Step 3: Train Model
        logger.info("[bold]Phase 3: Training ML Model[/bold]", extra={"markup": True})
        estimator = DebtEstimator()
        try:
            report = estimator.train(processed_data)
            console.print("\n[bold]Model Evaluation Report:[/bold]")
            console.print(report)
        except Exception as e:
            logger.error(f"Model training failed: {e}")

        # Step 4: Estimate Current Debt (For a specific file or aggregate)
        logger.info("[bold]Phase 4: Estimating Technical Debt[/bold]", extra={"markup": True})
        
        # If no specific file is requested, we analyze the latest version of an example file from the dataset
        target_code = ""
        target_name = ""
        
        if file_path:
            full_path = os.path.join(repo_path, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    target_code = f.read()
                target_name = file_path
            else:
                logger.error(f"File not found: {full_path}")
                raise typer.Exit(code=1)
        else:
            # Just take the first valid one as an example
            example = processed_data[0]
            target_code = example['source_code']
            target_name = example['filename']
            logger.info(f"No specific file provided. Analyzing example file from history: {target_name}")

        current_metrics = analyzer.analyze_code(target_code)
        debt_results = estimator.estimate_debt(current_metrics)
        
        # Step 5: Display Results beautifully
        display_results(target_name, current_metrics, debt_results)

    except Exception as e:
        logger.exception("An error occurred during analysis.")
        raise typer.Exit(code=1)

def display_results(file_name: str, metrics: dict, debt_results: dict):
    """Formats and prints the results using Rich."""
    console.print("\n")
    
    # Metrics Table
    metrics_table = Table(title=f"Metrics for [bold cyan]{file_name}[/bold cyan]")
    metrics_table.add_column("Metric", style="magenta")
    metrics_table.add_column("Value", justify="right", style="green")
    
    metrics_table.add_row("Lines of Code (LOC)", str(metrics.get('loc', 0)))
    metrics_table.add_row("Cyclomatic Complexity", f"{metrics.get('cyclomatic_complexity', 0):.2f}")
    metrics_table.add_row("Halstead Difficulty", f"{metrics.get('halstead_difficulty', 0):.2f}")
    metrics_table.add_row("Halstead Volume", f"{metrics.get('halstead_volume', 0):.2f}")
    metrics_table.add_row("Number of Functions", str(metrics.get('num_functions', 0)))
    
    console.print(metrics_table)
    
    # Debt Index Panel
    score = debt_results['health_score']
    index = debt_results['technical_debt_index']
    
    color = "green" if index == "Low" else "yellow" if index == "Medium" else "red"
    
    debt_text = f"[bold]Health Score:[/bold] [{color}]{score}/100[/{color}]\n"
    debt_text += f"[bold]Debt Index:[/bold] [{color}]{index}[/{color}]\n"
    debt_text += f"[bold]Bug Probability:[/bold] {debt_results['bug_probability']*100:.1f}%\n\n"
    
    debt_text += "[bold]Refactoring Suggestions:[/bold]\n"
    for sug in debt_results['refactoring_suggestions']:
        debt_text += f"• {sug}\n"
        
    console.print(Panel(debt_text, title="[bold blue]Technical Debt Report[/bold blue]", border_style="blue"))

if __name__ == "__main__":
    app()
