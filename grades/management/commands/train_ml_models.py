"""Management command to train ML models."""
import os
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Train ML models for student analytics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--samples',
            type=int,
            default=2000,
            help='Number of synthetic samples to generate for training'
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting ML model training...')
        
        try:
            # Import the training script
            import sys
            ml_scripts_path = os.path.join(settings.BASE_DIR, 'ml', 'scripts')
            sys.path.append(ml_scripts_path)
            
            from train_models import train_and_save_models
            
            samples = options['samples']
            self.stdout.write(f'Training models with {samples} samples...')
            
            # Train the models
            train_and_save_models(samples=samples)
            
            self.stdout.write(
                self.style.SUCCESS('Successfully trained and saved ML models!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error training models: {str(e)}')
            )