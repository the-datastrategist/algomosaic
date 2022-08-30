import os
import kfp
import configs
from datetime import datetime as dt


# Load Kubeflow client
PIPELINE_LOCAL_STORAGE_DIRECTORY = 'pipelines/compiled_pipelines'
HOME_DIRECTORY = os.getcwd()
DEFAULT_PAGE_SIZE = 200

client = kfp.Client(host=configs.KFP_CLIENT_HOST)


class pipelineLoader():
    """Loads pipelines to Kubeflow without a manual handling.

    loader = pipelineLoader(
        pipeline_function=my_function,
        pipeline_name='this_is_my_pipeline'
        pipeline_description='This is a dope pipeline.'
    )
    """
    def __init__(
        self,
        pipeline_function,
        pipeline_name,
        pipeline_description=None,
        local_storage_directory=PIPELINE_LOCAL_STORAGE_DIRECTORY,
        home_directory=HOME_DIRECTORY,
    ):
        self.client = kfp.Client(host=configs.KFP_CLIENT_HOST)
        self.pipeline_function=pipeline_function
        self.pipeline_name=pipeline_name
        self.pipeline_description=pipeline_description
        self.local_storage_directory=local_storage_directory
        self.home_directory=home_directory
        self.pipeline_path=os.path.join(
            self.home_directory,
            self.local_storage_directory,
            "{}.zip".format(self.pipeline_name)
        )

    def compile_pipeline(self):
        kfp.compiler.Compiler().compile(
            self.pipeline_function,
            self.pipeline_path
        )
        print("RUNNING: Compiled pipeline and loaded to {}".format(
            self.pipeline_path
        ))

    def set_pipelines(self):
        pipeline_list = self.client.list_pipelines(page_size=DEFAULT_PAGE_SIZE)
        self.pipelines = pipeline_list.pipelines
        self.pipeline_names = [p.name for p in self.pipelines]
        self.pipeline_ids = [p.id for p in self.pipelines]

    def _check_pipeline_exists(self):
        return self.pipeline_name in self.pipeline_names

    def load_pipeline(self):
        self.compile_pipeline()
        self.set_pipelines()

        try:
            if self._check_pipeline_exists():
                # Load new version of the pipeline
                print("RUNNING: Loading pipeline version: {}.".format(self.pipeline_name))
                self.pipeline_version_name="{}_version_at_{}".format(
                    self.pipeline_name, dt.now().strftime('%Y-%m-%dT%H:%M:%S')
                )
                self.load_response = self.client.upload_pipeline_version(
                    pipeline_package_path=self.pipeline_path,
                    pipeline_version_name=self.pipeline_version_name,
                    pipeline_name=self.pipeline_name
                )
                print("SUCCESS: Load successful.\n{}".format(self.load_response))

            else:
                # Load new pipeline
                print("RUNNING: Loading pipeline: {}.".format(
                    self.pipeline_name
                ))
                self.load_response = self.client.upload_pipeline(
                    pipeline_package_path=self.pipeline_path,
                    pipeline_name=self.pipeline_name,
                    description=self.pipeline_description
                )
                print("SUCCESS: Load successful.\n{}".format(self.load_response))

        except Exception as e:
            print("ERROR: {}.".format(e))
