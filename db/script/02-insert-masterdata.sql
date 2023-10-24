\connect blog;

\c blog;

INSERT INTO public.tag (id,title,meta_title,icon_image_url) VALUES
	 ('2b3fa430-295d-4027-859a-165a5170c8a4','aws_icon.svg','aws','https://haruki-blog-image.s3.amazonaws.com/icons/aws_icon.svg'),
	 ('fb11c458-3dbe-4562-84b1-435fc5a0505a','docker_icon.svg','docker','https://haruki-blog-image.s3.amazonaws.com/icons/docker_icon.svg'),
	 ('6872bb7b-7faa-4d13-9193-8df227ce84b4','go_icon.svg','go','https://haruki-blog-image.s3.amazonaws.com/icons/go_icon.svg'),
	 ('9ce47ebd-9e36-4262-a7d5-a24c5c38d2ac','mysql_icon.svg','mysql','https://haruki-blog-image.s3.amazonaws.com/icons/mysql_icon.svg'),
	 ('13bd6f3c-84f2-4806-9602-d5add7cdea1e','python_icon.svg','python','https://haruki-blog-image.s3.amazonaws.com/icons/python_icon.svg'),
	 ('d1c0d053-13dd-4672-8bf6-2642f203d9bf','react_icon.svg','react','https://haruki-blog-image.s3.amazonaws.com/icons/react_icon.svg'),
	 ('eeb6202f-de46-4c23-afe4-b9eaf993a6dc','typescript_icon.svg','typescript','https://haruki-blog-image.s3.amazonaws.com/icons/typescript_icon.svg');
