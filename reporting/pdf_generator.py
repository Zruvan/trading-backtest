"""PDF report generation for backtest results."""
import os
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import matplotlib.pyplot as plt
from io import BytesIO

from reporting.visualizations import BacktestVisualizer


class PDFReportGenerator:
    """Generates PDF reports for backtest results."""
    
    def __init__(self, results: Dict[str, Any], output_path: str):
        """
        Initialize report generator.
        
        Args:
            results: Backtest results dictionary
            output_path: Path to save PDF report
        """
        self.results = results
        self.output_path = output_path
        self.doc = SimpleDocTemplate(output_path, pagesize=letter)
        self.story = []
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        self.visualizer = BacktestVisualizer()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2ca02c'),
            spaceAfter=12
        ))
    
    def generate_report(self):
        """Generate the complete PDF report."""
        # Title page
        self._add_title_page()
        
        # Executive summary
        self._add_executive_summary()
        
        # Performance metrics
        self._add_performance_metrics()
        
        # Visualizations
        self._add_visualizations()
        
        # Trade analysis
        self._add_trade_analysis()
        
        # Strategy details
        self._add_strategy_details()
        
        # Build PDF
        self.doc.build(self.story)
        print(f"Report saved to: {self.output_path}")
    
    def _add_title_page(self):
        """Add title page to report."""
        # Title
        title = Paragraph(
            f"Backtest Report: {self.results['strategy']['name']}",
            self.styles['CustomTitle']
        )
        self.story.append(title)
        self.story.append(Spacer(1, 0.5*inch))
        
        # Date
        date_text = Paragraph(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            self.styles['Normal']
        )
        self.story.append(date_text)
        self.story.append(Spacer(1, 0.3*inch))
        
        # Basic info
        info_data = [
            ['Backtest Period:', f"{self.results['strategy'].get('start_date', 'N/A')} to {self.results['strategy'].get('end_date', 'N/A')}"],
            ['Initial Capital:', f"${self.results['strategy']['initial_capital']:,.2f}"],
            ['Rebalance Frequency:', self.results['strategy']['rebalance_frequency'].capitalize()],
            ['Commission:', f"{self.results['strategy']['commission']*100:.2f}%"],
            ['Slippage:', f"{self.results['strategy']['slippage']*100:.2f}%"]
        ]
        
        info_table = Table(info_data, colWidths=[2.5*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        self.story.append(info_table)
        self.story.append(PageBreak())
    
    def _add_executive_summary(self):
        """Add executive summary section."""
        self.story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Key metrics summary
        total_return = self.results.get('total_return', 0) * 100
        annualized_return = self.results.get('annualized_return', 0) * 100
        sharpe_ratio = self.results.get('sharpe_ratio', 0)
        max_drawdown = self.results.get('max_drawdown', 0) * 100
        
        summary_text = f"""
        The {self.results['strategy']['name']} strategy achieved a total return of {total_return:.2f}% 
        with an annualized return of {annualized_return:.2f}%. The strategy's risk-adjusted performance, 
        measured by the Sharpe ratio, was {sharpe_ratio:.2f}. The maximum drawdown experienced during 
        the backtest period was {abs(max_drawdown):.2f}%.
        """
        
        self.story.append(Paragraph(summary_text, self.styles['Normal']))
        self.story.append(Spacer(1, 0.3*inch))
    
    def _add_performance_metrics(self):
        """Add performance metrics section."""
        self.story.append(Paragraph("Performance Metrics", self.styles['SectionHeader']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Create metrics table
        metrics_data = [
            ['Metric', 'Value'],
            ['Total Return', f"{self.results.get('total_return', 0)*100:.2f}%"],
            ['Annualized Return', f"{self.results.get('annualized_return', 0)*100:.2f}%"],
            ['Volatility', f"{self.results.get('volatility', 0)*100:.2f}%"],
            ['Sharpe Ratio', f"{self.results.get('sharpe_ratio', 0):.3f}"],
            ['Sortino Ratio', f"{self.results.get('sortino_ratio', 0):.3f}"],
            ['Max Drawdown', f"{self.results.get('max_drawdown', 0)*100:.2f}%"],
            ['Calmar Ratio', f"{self.results.get('calmar_ratio', 0):.3f}"],
            ['Total Trades', f"{self.results.get('total_trades', 0)}"],
            ['Win Rate', f"{self.results.get('win_rate', 0)*100:.1f}%"],
        ]
        
        if 'benchmark_return' in self.results:
            metrics_data.extend([
                ['Benchmark Return', f"{self.results['benchmark_return']*100:.2f}%"],
                ['Alpha', f"{self.results.get('alpha', 0)*100:.2f}%"],
                ['Beta', f"{self.results.get('beta', 1):.3f}"],
            ])
        
        metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        self.story.append(metrics_table)
        self.story.append(PageBreak())
    
    def _add_visualizations(self):
        """Add visualization section."""
        self.story.append(Paragraph("Performance Visualizations", self.styles['SectionHeader']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Portfolio value chart
        if 'portfolio_values' in self.results:
            fig = self.visualizer.plot_portfolio_value(
                self.results['portfolio_values'],
                title="Portfolio Value Over Time"
            )
            self._add_figure_to_story(fig, "Portfolio value growth over the backtest period")
            
            # Returns distribution
            returns = self.results['portfolio_values']['value'].pct_change().dropna()
            fig = self.visualizer.plot_returns_distribution(
                returns,
                title="Daily Returns Distribution"
            )
            self._add_figure_to_story(fig, "Distribution of daily returns")
            
            # Drawdown chart
            fig = self.visualizer.plot_drawdown(
                self.results['portfolio_values'],
                title="Portfolio Drawdown"
            )
            self._add_figure_to_story(fig, "Underwater equity curve showing drawdowns")
            
            # Monthly returns heatmap
            fig = self.visualizer.plot_monthly_returns_heatmap(
                self.results['portfolio_values'],
                title="Monthly Returns Heatmap"
            )
            self._add_figure_to_story(fig, "Monthly returns by year")
    
    def _add_trade_analysis(self):
        """Add trade analysis section."""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Trade Analysis", self.styles['SectionHeader']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Add trade statistics
        trade_stats = f"""
        Total number of trades executed: {self.results.get('total_trades', 0)}
        Winning trades: {self.results.get('winning_trades', 0)}
        Win rate: {self.results.get('win_rate', 0)*100:.1f}%
        """
        
        self.story.append(Paragraph(trade_stats, self.styles['Normal']))
    
    def _add_strategy_details(self):
        """Add strategy details section."""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Strategy Details", self.styles['SectionHeader']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Strategy parameters
        params_text = "Strategy Parameters:"
        self.story.append(Paragraph(params_text, self.styles['Heading3']))
        
        for key, value in self.results['strategy'].items():
            if key not in ['name']:
                param_text = f"• {key.replace('_', ' ').title()}: {value}"
                self.story.append(Paragraph(param_text, self.styles['Normal']))
    
    def _add_figure_to_story(self, fig: plt.Figure, caption: str = ""):
        """Add matplotlib figure to PDF story."""
        # Save figure to BytesIO
        img_buffer = BytesIO()
        fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)
        
        # Add to story
        img = Image(img_buffer, width=6*inch, height=4*inch)
        self.story.append(img)
        
        if caption:
            caption_style = ParagraphStyle(
                'Caption',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
            self.story.append(Spacer(1, 0.1*inch))
            self.story.append(Paragraph(caption, caption_style))
        
        self.story.append(Spacer(1, 0.3*inch))