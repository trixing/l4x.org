/*
 * Test program for the POSIT algorithm with OpenCV
 * Freestyle after the example of the opencv-wiki page
 *
 * The program performs a 3D to 2D transformation and uses
 * the POSIT algorithm to recover the 3D pose. Afterwards it
 * projects this estimated pose back to the 2D space and plots
 * the difference. The translation and rotation are controllable
 * by trackbars. In theory both should match exactly.
 *
 * g++ `pkg-config --libs --cflags opencv` -Wall -pthread posit.cpp -o posit
 *
 * (c) 2010 Jan Dittmer <jdi@l4x.org>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; version 2
 * of the License.
 *
 */
#include <opencv/cv.h>
#include <opencv/highgui.h>
#include <stdio.h>

#define W 640
#define H 480
#define GREEN CV_RGB(0,255,0)
#define RED CV_RGB(255,0,0)
#define CYAN CV_RGB(0,255,255)

#define WIN "posit"
#define PI 3.14159265

#define ANGLE(rad) (rad*180.0/PI)

#define L_FRONT_ARM 220.0f
#define L_RIGHT 180.0f
#define L_LEFT L_RIGHT
#define L_ANTENNA 300.0f
#define D_ANTENNA  30.0f
#define H_ARM 10.0f

// the Model
#define N 4
CvPoint3D32f modelPoints[N] = {
		{ 0.0f, 0.0f, 0.0f },
		{ -L_RIGHT, -H_ARM, L_FRONT_ARM},
		{  L_LEFT,  -H_ARM, L_FRONT_ARM},
		{ 0.0f, -L_ANTENNA - H_ARM, L_FRONT_ARM + D_ANTENNA}
	};


// camera parameters
//double _intrinsics[9] =
//	{ 531.9163709104515192, 0., 299.9301060718951817, 0.,
//	530.9958838480581562, 245.9404069432019924, 0., 0., 1. };
double _intrinsics[9] =
	{ 530, 0., W/2,
	  0., 530, H/2,
	  0., 0., 1. };
int focalPoint = 530;
CvMat intrinsics = cvMat(4,4,CV_64F, _intrinsics);


void make_projection(int n, CvPoint3D32f *model, CvMat *pose, CvPoint2D32f *projection) {

	for ( int  p=0; p<n; p++ ) {
		double _mp[] =  { model[p].x, model[p].y, model[p].z, 1.0f };
		CvMat mp = cvMat( 4, 1, CV_64F, _mp );
		double _p3d[4];
		CvMat p3d = cvMat( 4, 1, CV_64F, _p3d );
		//Transform the points from model space coordinates to camera space
		//The pose must be transposed because is in OpenGL format
		cvGEMM( pose, &mp, 1.0, NULL, 0.0, &p3d, CV_GEMM_A_T );
		//Project the transformed 3D points
		//printf("G %.6f,%.6f,%.6f\n",point3D[0],point3D[1],point3D[2]);
		CvPoint2D32f p2d = cvPoint2D32f( 0.0, 0.0 );
		if ( _p3d[2] != 0 ) {
			p2d.x = cvmGet( &intrinsics, 0, 0 ) * _p3d[0] / _p3d[2]; // fx
			p2d.y = cvmGet( &intrinsics, 1, 1 ) * _p3d[1] / _p3d[2]; // fy
		}
		projection[p] = p2d;
	}
}

void posit(int n, CvPoint3D32f *model, CvPoint2D32f *projection, double *tvec, double *rvec) {
// reconstructionm now that modelPoints are there...
	float _prmat[9];
	CvMat prmat = cvMat(3,3,CV_32F,_prmat);

	float _prvec[3];
	CvMat prvec = cvMat(3,1,CV_32F,_prvec);

	float _ptvec[3];
	CvMat ptvec = cvMat(3,1,CV_32F,_ptvec);
	CvPOSITObject *positObject = cvCreatePOSITObject( &model[0], 4 );
	CvTermCriteria criteria = cvTermCriteria(CV_TERMCRIT_EPS | CV_TERMCRIT_ITER, 400, 1.0e-5f);
	cvPOSIT( positObject, &projection[0], focalPoint, criteria, _prmat, _ptvec );
	cvRodrigues2(&prmat, &prvec);

	for(int i = 0; i < 3; i++) {
		tvec[i] = _ptvec[i];
		rvec[i] = _prvec[i];
	}

}

void tr_pose(double *_tvec, double *_rvec, double *pose) {
	double _rmat[9];
	CvMat rmat = cvMat(3,3,CV_64F,_rmat);
	CvMat rvec = cvMat(3,1,CV_64F,_rvec);

	for(int i = 0; i < 3; i++) {
		pose[12+i] = _tvec[i];
	}
	cvRodrigues2(&rvec,&rmat);
	for(int i = 0; i < 3; i++) {
		pose[i] = _rmat[i];
		pose[i+4] = _rmat[i+3];
		pose[i+8] = _rmat[i+6];
	}
	pose[3] = 0;
	pose[7] = 0;
	pose[11] = 0;
	pose[15] = 0;
}

int main(int argc, char **argv) {
#define SHIFT 5000
	int c,i;
	char s[1024], *t;


	double _rvec[3] = { 0, 0, 0 };
	double _tvec[3] = { 0, 0, 0 };

	double _prvec[3] = { 0, 0, 0 };
	//CvMat prvec = cvMat(3,1,CV_64F,_prvec);

	double _ptvec[3] = { 0, 0, 0 };
	//CvMat ptvec = cvMat(3,1,CV_64F,_ptvec);

	double _ppose[16];
	CvMat ppose = cvMat( 4, 4, CV_64F, _ppose );

	int _drvec[3] = { 180, 180, 180 };
	int _itvec[3] = {SHIFT, SHIFT, SHIFT + 1000};

	double _pose[16] = {
		1,0,0,0, // 0 - 3 R
		0,1,0,0, // 4 - 7 R
		0,0,1,0, // 8 - 11 R
		0,10,1000,0  //12 - 15 T
	};
	CvMat pose = cvMat( 4, 4, CV_64F, _pose );

	CvPoint2D32f projectedPoints[N];
	CvPoint2D32f pprojectedPoints[N];

	CvFont defFont;
	cvInitFont(&defFont, CV_FONT_HERSHEY_COMPLEX_SMALL, 0.8f, 0.8f, 0, 1, 1);

	IplImage *img = cvCreateImage(cvSize(W,H),8,3);

	cvNamedWindow(WIN, CV_WINDOW_AUTOSIZE);
	cvCreateTrackbar( "Rot. X", WIN, &_drvec[0], 360, 0 );
	cvCreateTrackbar( "Rot. Y", WIN, &_drvec[1], 360, 0 );
	cvCreateTrackbar( "Rot. Z", WIN, &_drvec[2], 360, 0 );

	cvCreateTrackbar( "Pos. X", WIN, &_itvec[0], 2*SHIFT, 0 );
	cvCreateTrackbar( "Pos. Y", WIN, &_itvec[1], 2*SHIFT, 0 );
	cvCreateTrackbar( "Pos. Z", WIN, &_itvec[2], 2*SHIFT, 0 );
	cvCreateTrackbar( "Focal Point", WIN, &focalPoint, 1200, 0 );
	printf("Press ESC to exit\n");
	while(c != 27) {
		cvZero(img);

		for(i = 0; i < 3; i++) {
			_rvec[i] = ((double)_drvec[i] - 180.0)*PI/180.0;
			_tvec[i] = _itvec[i] - SHIFT;
		}

		tr_pose(_tvec,_rvec,_pose);

		make_projection(N,modelPoints, &pose, projectedPoints);

		posit(N, modelPoints, projectedPoints, _ptvec, _prvec);
		for(i = 0; i < 3; i++) {
			_prvec[i] *= -1;
		}

		tr_pose(_ptvec,_prvec,_ppose);

		make_projection(N,modelPoints, &ppose, pprojectedPoints);

		for(int i = 0; i < N; i++) {
			cvCircle(img,cvPoint( projectedPoints[i].x + W/2, projectedPoints[i].y + H/2), 4,GREEN, 2);
			cvCircle(img,cvPoint( pprojectedPoints[i].x + W/2, pprojectedPoints[i].y + H/2), 4,CYAN, 2);
		}

		t = s;
		t += sprintf(s,"T  %.1f %.1f %.1f ",_tvec[0],_tvec[1],_tvec[2]);
		t += sprintf(t,"R %.1f %.1f %.1f ",ANGLE(_rvec[0]),ANGLE(_rvec[1]),ANGLE(_rvec[2]));
		cvPutText(img, s, cvPoint(0,20),&defFont, GREEN);

		t = s;
		t += sprintf(t,"T* %.1f %.1f %.1f ",_ptvec[0],_ptvec[1],_ptvec[2]);
		t += sprintf(t,"R* %.1f %.1f %.1f",ANGLE(_prvec[0]),ANGLE(_prvec[1]),ANGLE(_prvec[2]));
		cvPutText(img, s, cvPoint(0,40),&defFont, CYAN);

		//printf("%s\n",s);
		cvShowImage(WIN, img);
		c = cvWaitKey(50) & 0x00ff;
	}

	return 0;
}
