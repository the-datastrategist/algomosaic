import os
import yaml
import argparse
import kfp
import kfp.components as comp
import configs
from algom.kubeflow import utils


DEFAULT_PAGE_SIZE = 1000


# Load Kubeflow client
client = kfp.Client(host=configs.KFP_CLIENT_HOST)


class pipelineManager():
    """Create or update Kubeflow pipelines.

    Specfify pipeline parameters and this function will create or
    update a recurring run to Kubeflow.
    """
    
    def __init__(
        self,
        job_name,
        pipeline_name,
        params={},
        experiment_name='Default',
        experiment_id=None,
        pipeline_id=None,        
        version_id=None,
        description=None,
        start_time=None, 
        end_time=None,
        interval_second=None, 
        cron_expression=None, 
        max_concurrency=1,
        no_catchup=True, 
        enabled=True,
        status='Enabled'
    ):
        self.client = kfp.Client(host=configs.KFP_CLIENT_HOST)
        self.jobs_client = self.client.jobs
        self.job_name = job_name
        self.job_ids = self._get_job_ids()
        self.pipeline_name = pipeline_name
        self.experiments_list = self.client.list_experiments().experiments
        self.experiment_id = experiment_id or self._get_experiment_id(experiment_name)
        self.pipeline_id = pipeline_id or self._get_pipeline_id(pipeline_name)
        self.version_id = version_id or self._get_version_id()
        self.experiment_name = experiment_name
        self.params = params
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.interval_second = interval_second
        self.cron_expression = cron_expression
        self.max_concurrency = max_concurrency
        self.no_catchup = no_catchup
        self.enabled = enabled
        self.status = status

    def _get_experiment_id(self, experiment_name):
        return [e.id for e in self.experiments_list if e.name == experiment_name][0]

    def _get_pipeline_id(self, pipeline_name):
        try:
            return self.client.get_pipeline_id(pipeline_name)
        except:
            return None
    
    def _get_version_id(self):
        try:
            return utils.get_latest_pipeline_version(
                self.pipeline_id, self.pipeline_name
            )
        except:
            return None

    def _check_job_name_match(self):
        return any([
            j.name==self.job_name for j in \
            self.jobs_client.list_jobs(page_size=DEFAULT_PAGE_SIZE).jobs if j.enabled
        ])

    def _get_job_ids(self):
        return [
            j.id for j in self.jobs_client.list_jobs(page_size=DEFAULT_PAGE_SIZE).jobs \
            if j.name==self.job_name
        ]

    def enable_job(self):
        self.job_ids = self._get_job_ids()
        for job in self.job_ids:
            self.jobs_client.enable_job(id=job)

    def disable_job(self):
        self.job_ids = self._get_job_ids()
        for job in self.job_ids:
            self.jobs_client.disable_job(id=job)

    def delete_job(self):
        self.job_ids = self._get_job_ids()
        for job in self.job_ids:
            self.jobs_client.delete_job(id=job)

    def create_job(self):
        self.job = self.client.create_recurring_run(
            experiment_id=self.experiment_id, 
            job_name=self.job_name,
            description=self.description, 
            start_time=self.start_time, 
            end_time=self.end_time, 
            interval_second=self.interval_second, 
            cron_expression=self.cron_expression, 
            max_concurrency=self.max_concurrency,
            no_catchup=self.no_catchup, 
            params=self.params,
            pipeline_id=self.pipeline_id,
            version_id=self.version_id,
            enabled=self.enabled
        )
        self.job_ids = self._get_job_ids()

    def create_run(self):
        self.job = self.client.run_pipeline(
            experiment_id=self.experiment_id,
            job_name=self.job_name,
            params=self.params,
            pipeline_id=self.pipeline_id,
            version_id=self.version_id,
            pipeline_root=None
        )

    def update_job(self):
        job_match = self._check_job_name_match()
        status = str(self.status).lower()

        # If job_name exists ...
        if job_match and status=='enabled':
            print("RUNNING: Enabling {} in {}.".format(self.job_name, self.experiment_name))
            self.enable_job()
        elif job_match and status=='disabled':
            print("RUNNING: Disabling {} in {}.".format(self.job_name, self.experiment_name))
            self.disable_job()
        elif job_match and status=='update':
            print("RUNNING: Updating {} in {}.".format(self.job_name, self.experiment_name))
            self.delete_job()
            self.create_job()
        elif job_match and status=='delete':
            print("RUNNING: Deleting {} in {}.".format(self.job_name, self.experiment_name))
            self.delete_job()

        # If job_name doesn't exist ...
        elif not job_match and status=='disabled':
            print("RUNNING: Creating {} in {}.".format(self.job_name, self.experiment_name))
            print("RUNNING: Disabling {} in {}.".format(self.job_name, self.experiment_name))
            self.create_job()
            self.disable_job()
        else:
            print("RUNNING: Creating {} in {}.".format(self.job_name, self.experiment_name))
            self.create_job()


class pipelineYaml():
    """Load multiple Kubeflow pipelines from a YAML file.
    """
    
    def __init__(self, file):
        self.file=file
        self.pipeline_entries=self._get_pipeline_entries()
        self.update_pipelines()

    def _get_pipeline_entries(self):
        inputs_file = open(self.file, 'r')
        return yaml.load(inputs_file)

    def _swap_nones(self, entry):
        """Convert none strings to None
        """
        d = {}
        for k, v in entry.items():
            if isinstance(v, dict):
                dd={}
                for kk, vv in v.items():
                    dd[kk] = None if str(vv).lower()=='none' else vv
                d[k] = dd
            else:
                d[k] = None if str(v).lower()=='none' else v
        return d

    def update_pipelines(self):
        for entry in self.pipeline_entries:
            print("RUNNING: Loading {} to Kubeflow pipelines.".format(entry.get('job_name')))
            entry = self._swap_nones(entry)
            manager = pipelineManager(
                job_name=entry.get('job_name'),
                pipeline_name=entry.get('pipeline_name'),
                params=entry.get('params', {}),
                experiment_name=entry.get('experiment_name', 'Default'),
                version_id=entry.get('version_id'),
                description=entry.get('description'),
                start_time=entry.get('start_time'), 
                end_time=entry.get('end_time'),
                interval_second=entry.get('interval_second'), 
                cron_expression=entry.get('cron_expression'),
                max_concurrency=entry.get('max_concurrency', 1),
                no_catchup=entry.get('no_catchup', True), 
                enabled=entry.get('enabled', True),
                status=entry.get('status', 'disabled')
            )
            manager.update_job()


if __name__ == '__main__':

    # Add and parse bash arguments
    parser = argparse.ArgumentParser(
        description="Create or update Kubeflow pipelines from YAML."
    )
    parser.add_argument(
        '-file',
        type=str,
        metavar='-f',
        default=None,
        help='',
    )
    args = parser.parse_args()

    # Load pipelines
    loader = pipelineYaml(args.file)
