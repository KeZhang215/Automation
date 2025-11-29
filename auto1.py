#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Securities Lending Position Adjustment Journal Generator
证券借贷项目头寸调整日记账自动生成工具
"""

import pandas as pd
from datetime import datetime
from pathlib import Path


class JournalGenerator:
    """Generate journals for position adjustments in securities lending program"""

    def __init__(self, output_dir="output"):
        """
        Initialize journal generator

        Args:
            output_dir: Output directory path
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def load_position_data(self, file_path):
        """
        Load position data from file

        Args:
            file_path: Path to data file (CSV or Excel)

        Returns:
            DataFrame: Position data
        """
        file_path = Path(file_path)

        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        print(f"✓ Loaded {len(df)} records")
        return df

    def calculate_adjustments(self, current_positions, previous_positions=None):
        """
        Calculate position adjustments

        Args:
            current_positions: Current position data
            previous_positions: Previous day position data (optional)

        Returns:
            DataFrame: Adjustment data
        """
        if previous_positions is not None:
            # Merge current and previous data to calculate changes
            merged = pd.merge(
                current_positions,
                previous_positions,
                on=['security_id', 'account'],
                how='outer',
                suffixes=('_current', '_previous')
            ).fillna(0)

            merged['quantity_change'] = (
                merged['quantity_current'] - merged['quantity_previous']
            )
            merged['value_change'] = (
                merged['value_current'] - merged['value_previous']
            )

            # Keep only records with changes
            adjustments = merged[
                (merged['quantity_change'] != 0) | (merged['value_change'] != 0)
            ].copy()
        else:
            # If no previous data, all current positions are new
            adjustments = current_positions.copy()
            adjustments['quantity_change'] = adjustments['quantity']
            adjustments['value_change'] = adjustments['value']

        return adjustments

    def generate_journal_entries(self, adjustments, date=None):
        """
        Generate journal entries

        Args:
            adjustments: Position adjustment data
            date: Journal date (defaults to today)

        Returns:
            DataFrame: Journal entries
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        entries = []

        for _, row in adjustments.iterrows():
            security_id = row.get('security_id', row.get('security_id_current', 'UNKNOWN'))
            account = row.get('account', row.get('account_current', 'UNKNOWN'))
            quantity_change = row['quantity_change']
            value_change = row['value_change']

            if quantity_change > 0:
                # Borrowed securities increase
                entries.append({
                    'date': date,
                    'security_id': security_id,
                    'account': account,
                    'debit_account': 'Securities Borrowed',
                    'credit_account': 'Payable for Securities',
                    'quantity': abs(quantity_change),
                    'amount': abs(value_change),
                    'description': f'Borrow securities {security_id}'
                })
            elif quantity_change < 0:
                # Borrowed securities decrease (return)
                entries.append({
                    'date': date,
                    'security_id': security_id,
                    'account': account,
                    'debit_account': 'Payable for Securities',
                    'credit_account': 'Securities Borrowed',
                    'quantity': abs(quantity_change),
                    'amount': abs(value_change),
                    'description': f'Return securities {security_id}'
                })

        journal_df = pd.DataFrame(entries)
        print(f"✓ Generated {len(journal_df)} journal entries")

        return journal_df

    def export_to_excel(self, journal_entries, filename=None):
        """
        Export journal entries to Excel

        Args:
            journal_entries: Journal data
            filename: Output filename (optional)

        Returns:
            Path: Export file path
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'journal_entries_{timestamp}.xlsx'

        output_path = self.output_dir / filename

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Main sheet: Journal entries
            journal_entries.to_excel(writer, sheet_name='Journal Entries', index=False)

            # Summary sheet: By security
            if not journal_entries.empty:
                summary = journal_entries.groupby('security_id').agg({
                    'quantity': 'sum',
                    'amount': 'sum'
                }).reset_index()
                summary.to_excel(writer, sheet_name='Summary by Security', index=False)

                # Summary sheet: By account
                account_summary = journal_entries.groupby('account').agg({
                    'quantity': 'sum',
                    'amount': 'sum'
                }).reset_index()
                account_summary.to_excel(writer, sheet_name='Summary by Account', index=False)

        print(f"✓ Exported to: {output_path}")
        return output_path

    def export_to_csv(self, journal_entries, filename=None):
        """
        Export journal entries to CSV

        Args:
            journal_entries: Journal data
            filename: Output filename (optional)

        Returns:
            Path: Export file path
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'journal_entries_{timestamp}.csv'

        output_path = self.output_dir / filename
        journal_entries.to_csv(output_path, index=False, encoding='utf-8-sig')

        print(f"✓ Exported to: {output_path}")
        return output_path


def create_sample_data():
    """Create sample data for testing"""
    sample_data = {
        'security_id': ['SH600000', 'SH600016', 'SH600036', 'SZ000001', 'SZ000002'],
        'security_name': ['SPDB', 'CMBC', 'CMB', 'PAB', 'Vanke A'],
        'account': ['ACC001', 'ACC001', 'ACC002', 'ACC002', 'ACC003'],
        'quantity': [10000, 5000, 8000, 12000, 15000],
        'value': [120000.00, 45000.00, 320000.00, 180000.00, 375000.00]
    }

    df = pd.DataFrame(sample_data)

    # Save sample data
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    sample_file = output_dir / 'sample_positions.csv'
    df.to_csv(sample_file, index=False, encoding='utf-8-sig')

    print(f"✓ Created sample data: {sample_file}")
    return sample_file


def main():
    """Main function - demonstration"""
    print("=" * 60)
    print("Securities Lending Journal Generator")
    print("=" * 60)
    print()

    # Create generator instance
    generator = JournalGenerator(output_dir='output')

    # Create sample data
    print("1. Creating sample data...")
    sample_file = create_sample_data()
    print()

    # Load position data
    print("2. Loading position data...")
    positions = generator.load_position_data(sample_file)
    print()

    # Calculate adjustments (assuming all positions are new)
    print("3. Calculating position adjustments...")
    adjustments = generator.calculate_adjustments(positions)
    print()

    # Generate journal entries
    print("4. Generating journal entries...")
    journal_entries = generator.generate_journal_entries(adjustments)
    print()

    # Export to Excel and CSV
    print("5. Exporting journals...")
    excel_file = generator.export_to_excel(journal_entries)
    csv_file = generator.export_to_csv(journal_entries)
    print()

    print("=" * 60)
    print("✓ Complete!")
    print("=" * 60)
    print()
    print("Generated files:")
    print(f"  - Excel: {excel_file}")
    print(f"  - CSV:   {csv_file}")
    print()
    print("Usage instructions:")
    print("  1. Save your position data as CSV or Excel")
    print("  2. Data should include columns: security_id, account, quantity, value")
    print("  3. Call: generator.load_position_data('your_file.csv')")
    print("  4. Follow the example workflow to generate journals")


if __name__ == '__main__':
    main()
