from collections import defaultdict, deque
import torch

try:
    # for python module
    from .dataset import Dataset
    from .train_dataset import TrainDataset
except (ImportError, SystemError):  # pragma: no cover
    # for python script
    from dataset import Dataset
    from train_dataset import TrainDataset


class AdapTestDataset(Dataset):

    def __init__(self, data,
                 num_students, num_questions):
        """
        Args:
            data: list, [(sid, qid, score)]
            concept_map: dict, concept map {qid: cid}
            num_students: int, total student number
            num_questions: int, total question number
        """
        super().__init__(data, num_students, num_questions)

        # initialize tested and untested set
        self._tested = None
        self._untested = None
        self.reset()

    def apply_selection(self, student_idx, question_idx):
        """ 
        Add one untested question to the tested set
        Args:
            student_idx: int
            question_idx: int
        """
        assert question_idx in self._untested[student_idx], \
            'Selected question not allowed'
        self._untested[student_idx].remove(question_idx)
        self._tested[student_idx].append(question_idx)

    def reset(self):
        """ 
        Set tested set empty
        """
        self._tested = defaultdict(deque)
        self._untested = defaultdict(set)
        for sid in self.data:
            self._untested[sid] = set(self.data[sid].keys())

    def get_score(self, student_idx, question_idx):
        """
        Get the score of a question for a student
        """
        return self.data[student_idx][question_idx]

    @property
    def tested(self):
        return self._tested

    @property
    def untested(self):
        return self._untested

    def get_tested_dataset(self, last=False):
        """
        Get tested data for training
        Args: 
            last: bool, True - the last question, False - all the tested questions
        Returns:
            TrainDataset
        """
        triplets = []
        for sid, qids in self._tested.items():
            if last:
                qid = qids[-1]
                triplets.append((sid, qid, self.data[sid][qid]))
            else:
                for qid in qids:
                    triplets.append((sid, qid, self.data[sid][qid]))
        return TrainDataset(triplets, self.num_students, self.num_questions)