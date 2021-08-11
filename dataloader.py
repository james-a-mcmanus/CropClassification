import numpy as np
import rasterio
from typing import Sequence, Optional, Callable, Any
from torch.utils.data import Dataset, DataLoader


class Dataset_Sent2(Dataset, Randomizable):
    """
    
    """
    # 
    # 
    # 
    def __init__(
        self,
        image_files: Sequence[str],
        seg_files: Optional[Sequence[str]] = None,
        dtype: Optional[np.dtype] = np.float32,
        ) -> None:
        """
        Initializes the dataset with the image and segmentation filename lists.
        Args:
            image_files: list of image filenames
            seg_files: if in segmentation task, list of segmentation filenames
        Raises:
            ValueError: When ``seg_files`` length differs from ``image_files``.
        """

        if seg_files is not None and len(image_files) != len(seg_files):
            raise ValueError(
                "Must have same the number of segmentation as image files: "
                f"images={len(image_files)}, segmentations={len(seg_files)}."
            )

        self.image_files = image_files
        self.seg_files = seg_files
        # here load the imgade with rasterio maybe ? And Then of course load all bands and convert the images and segmentations to arrays
        self.loader = rasterio.open()
        self.dtype = dtype
        self.set_random_state(seed=get_seed())

        self._seed = 0  # transform synchronization seed

    def __len__(self) -> int:
        return len(self.image_files)

    def randomize(self, data: Optional[Any] = None) -> None:
        self._seed = self.R.randint(np.iinfo(np.int32).max)

    def __getitem__(self, index: int):
        self.randomize()
        seg = None

        img = self.loader(self.image_files[index])
        if self.seg_files is not None:
            seg = self.loader(self.seg_files[index])
            # We need a one hot enconding. Not in torch. All computations here are currently nor on the gpu.
            seg = what.ever.OneHot()

        data = [img]
        
        if seg is not None:
            data.append(seg)
            
        if len(data) == 1:
            return data[0]

        return data
